import asyncio
from edgar import get_filings
from config import TARGET_FORMS, CHUNK_SIZES_CHARS
from .classifier import classify_chunks
from .storage import save_chunks, db

def chunk_text(text: str, chunk_size: int):
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]

async def process_batch(batch, accession_no, chunk_size_chars, only_keep_positives=False):
    results = await classify_chunks(batch)
    return await save_chunks(results, batch, accession_no, chunk_size_chars, only_keep_positives=only_keep_positives)

async def process_filing(filing, chunk_size_chars: int, only_keep_positives: bool = False):

    accession_no = filing.accession_no
    if db.exists(accession_no, chunk_size_chars):
        return
        
    try:
        text = filing.text()
    except Exception as e:
        print(f"Skipping {accession_no} due to parsing error: {e}")
        return
        
    if not text:
        return
    db.clear(accession_no, chunk_size_chars)

    chunks = list(chunk_text(text, chunk_size_chars))

    print(f"Processing {accession_no} with chunk size {chunk_size_chars}")
    
    BATCH_SIZE = 10
    tasks = []
    batch = []
    for chunk in chunks:
        if len(chunk) < chunk_size_chars * 0.5:
            continue
        batch.append(chunk)
        if len(batch) >= BATCH_SIZE:
            tasks.append(asyncio.create_task(process_batch(batch, accession_no, chunk_size_chars, only_keep_positives)))
            batch = []
    
    if batch:
        tasks.append(asyncio.create_task(process_batch(batch, accession_no, chunk_size_chars, only_keep_positives)))

    if tasks:
        results = await asyncio.gather(*tasks)
        total_kept = sum(results)
        print(f"Finished {accession_no} with chunk size {chunk_size_chars}. Kept {total_kept} chunks.")

    db.mark_processed(accession_no, chunk_size_chars)


def run_pipeline(limit: int = 1, only_keep_positives: bool = False):
    filings = get_filings(form=TARGET_FORMS)
    
    async def _run():
        for filing in filings[:limit]:
            for chunk_size in CHUNK_SIZES_CHARS:
                if db.exists(filing.accession_no, chunk_size):
                    continue
                await process_filing(filing, chunk_size, only_keep_positives)
    asyncio.run(_run())

if __name__ == "__main__":
    run_pipeline(limit=500, only_keep_positives=True)
