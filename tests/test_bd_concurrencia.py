import asyncio
import pytest
from sqlalchemy.exc import IntegrityError
from unittest.mock import AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_session_rollback_on_partial_failure():
    """
    Test that session.rollback() is called and prevents partial corrupt data
    when an insertion fails halfway.
    """
    session = AsyncMock()

    async def transactional_operation(session_mock):
        try:
            session_mock.add(MagicMock(id=1, status="pending"))
            raise IntegrityError("Unique constraint failed", None, None)
        except IntegrityError:
            await session_mock.rollback()
            raise

    with pytest.raises(IntegrityError):
        await transactional_operation(session)

    session.rollback.assert_awaited_once()
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_concurrent_expediente_closure():
    """
    Test concurrency handling when two async tasks attempt to close
    the same expediente simultaneously.
    """
    class Expediente:
        def __init__(self):
            self.status = "open"
            self._lock = asyncio.Lock()

        async def close(self):
            async with self._lock:
                if self.status == "closed":
                    raise ValueError("Expediente is already closed")
                await asyncio.sleep(0.01)
                self.status = "closed"

    expediente = Expediente()

    results = await asyncio.gather(
        expediente.close(),
        expediente.close(),
        return_exceptions=True
    )

    assert expediente.status == "closed"

    successes = [r for r in results if r is None]
    failures = [r for r in results if isinstance(r, ValueError)]

    assert len(successes) == 1
    assert len(failures) == 1
    assert str(failures[0]) == "Expediente is already closed"
