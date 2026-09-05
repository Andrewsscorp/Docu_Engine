from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import HTTPException
from datetime import datetime
from dateutil.relativedelta import relativedelta
import hashlib
import os
import xml.etree.ElementTree as ET
from app.services.audit_service import log_audit_sgdea_async
from fastapi import BackgroundTasks

class ExpedienteService:
    @staticmethod
    async def cerrar_expediente(
        expediente_id: str,
        tenant_id: str,
        user_id: str,
        ip_origen: str,
        db: AsyncSession,
        background_tasks: BackgroundTasks
    ):
        # 1. Lock Expediente and Fetch Metadata
        exp_res = await db.execute(text("""
            SELECT e.id, e.subserie_id, (e.estado = 'ABIERTO') as estado_abierto, e.codigo_expediente, e.nombre_expediente, 
                   e.fondo_id, e.serie_id, e.fecha_apertura,
                   s.retencion_ag
            FROM agn_expedientes e
            LEFT JOIN agn_subseries s ON e.subserie_id = s.id
            WHERE e.id = :eid FOR UPDATE OF e
        """), {"eid": expediente_id, "t": tenant_id})
        exp = exp_res.fetchone()
        if not exp:
            raise HTTPException(status_code=404, detail="Expediente no encontrado")
        if not exp.estado_abierto:
            raise HTTPException(status_code=403, detail="El expediente ya se encuentra cerrado")
            
        # 2. Check Completitud
        requeridas_res = await db.execute(text("""
            SELECT tipologia_id 
            FROM agn_expediente_tipologia 
            WHERE expediente_id = :eid AND obligatoria = TRUE
        """), {"eid": exp.id})
        req_ids = [str(r[0]) for r in requeridas_res.fetchall()]
        
        docs_res = await db.execute(text("""
            SELECT d.id, d.tipologia_id, d.hash_documento, d.file_hash, d.folio, d.folio_fin, d.file_name, d.created_at,
                   t.nombre_oficial 
            FROM documents d
            LEFT JOIN agn_tipologias t ON d.tipologia_id = t.id
            WHERE d.agn_expediente_id = :eid AND d.status IN ('COMPLETED', 'ARCHIVED')
            ORDER BY d.folio ASC
        """), {"eid": expediente_id, "t": tenant_id})
        docs = docs_res.fetchall()
        doc_tipos = [str(d.tipologia_id) for d in docs if d.tipologia_id]
        
        if len(docs) == 0:
            raise HTTPException(status_code=403, detail="Un expediente vacío (0 documentos) no puede ser cerrado o transferido. Debe contener al menos un documento.")
            
        faltantes = set(req_ids) - set(doc_tipos)
        if faltantes:
            raise HTTPException(status_code=403, detail="El expediente está INCOMPLETO. Faltan tipologías obligatorias por la TRD.")
            
        # 3. Calcular Fecha Cierre y Retención
        fecha_cierre_dt = datetime.utcnow()
        fecha_cierre_iso = fecha_cierre_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        fecha_apertura_iso = exp.fecha_apertura.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        retencion_ag_years = exp.retencion_ag or 0
        fecha_transferencia_dt = fecha_cierre_dt + relativedelta(years=retencion_ag_years)
        
        total_folios = 0
        if docs:
            last_doc = docs[-1]
            total_folios = last_doc.folio_fin if last_doc.folio_fin else last_doc.folio
            
        # 4. Generate XML Manifest
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
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
"""
        
        consecutivo = 1
        for d in docs:
            d_hash = d.file_hash or d.hash_documento or "HASH_ERROR"
            d_fecha = d.created_at.strftime("%Y-%m-%dT%H:%M:%SZ")
            xml_content += f"""  <Documento id="{d.id}">
      <OrdenConsecutivo>{consecutivo}</OrdenConsecutivo>
      <TipologiaDocumental>{d.nombre_oficial}</TipologiaDocumental>
      <NombreArchivo>{d.file_name}</NombreArchivo>
      <FechaIncorporacion>{d_fecha}</FechaIncorporacion>
      <FolioInicio>{d.folio}</FolioInicio>
      <FolioFin>{d.folio_fin if d.folio_fin else d.folio}</FolioFin>
      <Soporte>Electronico</Soporte>
      <HuellaCriptografica algoritmo="SHA-256">{d_hash}</HuellaCriptografica>
    </Documento>
"""
            consecutivo += 1
            
        xml_content += "  </ListaDocumentos>\n"
        
        raw_hash = hashlib.sha256(xml_content.encode()).hexdigest()
        xml_content += f"""  <HashIntegridad>{raw_hash}</HashIntegridad>\n</IndiceElectronico>"""
        
        # 5. Save XML
        upload_dir = os.path.join("uploads", str(tenant_id))
        os.makedirs(upload_dir, exist_ok=True)
        xml_filename = f"{expediente_id}_indice.xml"
        xml_path = os.path.join(upload_dir, xml_filename)
        
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
            
        # 6. DB Update
        await db.execute(text("""
            UPDATE agn_expedientes 
            SET estado = 'CERRADO', 
                estado_abierto = FALSE, 
                fecha_cierre = :fc,
                fecha_transferencia_central = :ftc,
                indice_xml_path = :xml_path,
                indice_xml_hash = :xml_hash
            WHERE id = :eid
        """), {
            "eid": expediente_id,
            "fc": fecha_cierre_dt,
            "ftc": fecha_transferencia_dt,
            "xml_path": xml_path,
            "xml_hash": raw_hash
        })
        
        await db.execute(text("""
            INSERT INTO agn_indice_electronico (expediente_id, accion, usuario_id, firma_indice)
            VALUES (:eid, 'CIERRE_EXPEDIENTE', :uid, :ihash)
        """), {"eid": expediente_id, "uid": user_id, "ihash": raw_hash})
        
        await db.commit()
        
        background_tasks.add_task(log_audit_sgdea_async, expediente_id, user_id, "CIERRE_EXPEDIENTE", ip_origen, {"hash_final_xml": raw_hash, "folios_cerrados": total_folios})
        
        return {"status": "success", "xml_hash": raw_hash}
