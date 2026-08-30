with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_endpoint = r'@router\.post\("/expedientes/\{expediente_id\}/cerrar"\).*?index_seed = f"\{prev_hash\}\{final_hash\}CERRAR_EXPEDIENTE".*?await db\.commit\(\).*?return JSONResponse\(\{"status": "success"\}\)'

new_endpoint = """@router.post("/expedientes/{expediente_id}/cerrar")
async def cerrar_expediente(
    expediente_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    session_data: dict = Depends(require_permission("documentos:editar")),
    db: AsyncSession = Depends(get_db_session)
):
    import hashlib
    import os
    import xml.etree.ElementTree as ET
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    # 1. Lock Expediente and Fetch Metadata
    exp_res = await db.execute(text('''
        SELECT e.id, e.subserie_id, (e.estado = 'ABIERTO') as estado_abierto, e.codigo_expediente, e.nombre_expediente, 
               e.fondo_id, e.serie_id, e.fecha_apertura,
               s.retencion_ag
        FROM agn_expedientes e
        LEFT JOIN agn_subseries s ON e.subserie_id = s.id
        WHERE e.id = :eid FOR UPDATE
    '''), {"eid": expediente_id})
    exp = exp_res.fetchone()
    if not exp:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
    if not exp.estado_abierto:
        raise HTTPException(status_code=403, detail="El expediente ya se encuentra cerrado")
        
    # 2. Check Completitud
    requeridas_res = await db.execute(text('''
        SELECT tipologia_id 
        FROM agn_subserie_tipologia 
        WHERE subserie_id = :sid AND obligatoria = TRUE
    '''), {"sid": exp.subserie_id})
    req_ids = [str(r[0]) for r in requeridas_res.fetchall()]
    
    docs_res = await db.execute(text('''
        SELECT d.id, d.tipologia_id, d.hash_documento, d.file_hash, d.folio, d.folio_fin, d.file_name, d.created_at,
               t.nombre_oficial 
        FROM documents d
        LEFT JOIN agn_tipologias t ON d.tipologia_id = t.id
        WHERE d.agn_expediente_id = :eid AND d.status IN ('COMPLETED', 'ARCHIVED')
        ORDER BY d.folio ASC
    '''), {"eid": expediente_id})
    docs = docs_res.fetchall()
    doc_tipos = [str(d.tipologia_id) for d in docs if d.tipologia_id]
    
    for rid in req_ids:
        if rid not in doc_tipos:
            raise HTTPException(status_code=403, detail="El expediente no cumple el 100% de la completitud documental. Faltan tipologías obligatorias.")
            
    # 3. Calcular Fecha Cierre y Retención
    fecha_cierre_dt = datetime.utcnow()
    fecha_cierre_iso = fecha_cierre_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    fecha_apertura_iso = exp.fecha_apertura.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Calcular fecha_transferencia_central = fecha_cierre + retencion_ag (años)
    retencion_ag_years = exp.retencion_ag or 0
    fecha_transferencia_dt = fecha_cierre_dt + relativedelta(years=retencion_ag_years)
    
    total_folios = 0
    if docs:
        last_doc = docs[-1]
        total_folios = last_doc.folio_fin if last_doc.folio_fin else last_doc.folio
        
    # 4. Generate XML Manifest (AGN XSD Standard)
    xml_content = f\"\"\"<?xml version="1.0" encoding="UTF-8"?>
<IndiceElectronico xmlns="urn:co:gov:agn:sgdea:indice:v1">
  <MetadatosExpediente>
    <Identificador>{exp.codigo_expediente}</Identificador>
    <Nombre>{exp.nombre_expediente}</Nombre>
    <CodigoFondo>{exp.fondo_id}</CodigoFondo>
    <CodigoSerie>{exp.serie_id}</CodigoSerie>
    <CodigoSubserie>{exp.subserie_id}</CodigoSubserie>
    <FechaApertura>{fecha_apertura_iso}</FechaApertura>
    <FechaCierre>{fecha_cierre_iso}</FechaCierre>
    <TotalFolios>{total_folios}</TotalFolios>
  </MetadatosExpediente>
  <ListaDocumentos>
\"\"\"
    
    consecutivo = 1
    for d in docs:
        d_hash = d.file_hash or d.hash_documento or "HASH_ERROR"
        d_fecha = d.created_at.strftime("%Y-%m-%dT%H:%M:%SZ")
        xml_content += f\"\"\"    <Documento id="{d.id}">
      <OrdenConsecutivo>{consecutivo}</OrdenConsecutivo>
      <TipologiaDocumental>{d.nombre_oficial}</TipologiaDocumental>
      <NombreArchivo>{d.file_name}</NombreArchivo>
      <FechaIncorporacion>{d_fecha}</FechaIncorporacion>
      <FolioInicio>{d.folio}</FolioInicio>
      <FolioFin>{d.folio_fin if d.folio_fin else d.folio}</FolioFin>
      <Soporte>Electronico</Soporte>
      <HuellaCriptografica algoritmo="SHA-256">{d_hash}</HuellaCriptografica>
    </Documento>
\"\"\"
        consecutivo += 1
        
    xml_content += "  </ListaDocumentos>\n"
    
    # Generate PKI Signature Hash
    raw_hash = hashlib.sha256(xml_content.encode()).hexdigest()
    # Mocking W3C XMLDSig standard payload inside FirmaIndice
    xml_content += f\"\"\"  <FirmaIndice>
    <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
      <SignedInfo>
         <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
         <SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha256"/>
      </SignedInfo>
      <SignatureValue>{raw_hash}</SignatureValue>
    </Signature>
  </FirmaIndice>
</IndiceElectronico>\"\"\"
    
    # 5. Save XML to Blob Storage
    upload_dir = os.path.join("uploads", str(session_data["tenant_id"]))
    os.makedirs(upload_dir, exist_ok=True)
    xml_filename = f"{expediente_id}_indice.xml"
    xml_path = os.path.join(upload_dir, xml_filename)
    
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
        
    # 6. Atomic DB Update
    await db.execute(text('''
        UPDATE agn_expedientes 
        SET estado = 'CERRADO', 
            fecha_cierre = :fc,
            fecha_transferencia_central = :ftc,
            indice_xml_path = :xml_path,
            indice_xml_hash = :xml_hash
        WHERE id = :eid
    '''), {
        "eid": expediente_id,
        "fc": fecha_cierre_dt,
        "ftc": fecha_transferencia_dt,
        "xml_path": xml_path,
        "xml_hash": raw_hash
    })
    
    # 7. Insert Indice Electronico log and Auditoria SGDEA
    await db.execute(text('''
        INSERT INTO agn_indice_electronico (expediente_id, accion, usuario_id, firma_indice)
        VALUES (:eid, 'CIERRE_EXPEDIENTE', :uid, :ihash)
    '''), {"eid": expediente_id, "uid": session_data["user_id"], "ihash": raw_hash})
    
    await db.commit()
    
    ip_origen = request.client.host if request.client else "unknown"
    background_tasks.add_task(log_audit_sgdea_async, expediente_id, session_data["user_id"], "CIERRE_EXPEDIENTE", ip_origen, {"hash_final_xml": raw_hash, "folios_cerrados": total_folios})
    
    return JSONResponse({"status": "success"})"""

content = re.sub(old_endpoint, new_endpoint, content, flags=re.DOTALL)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
