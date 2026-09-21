from edgar import current_filings
import os
from config import ExtractedSections
import json
import glob


class Db:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return
        self._initialized = True
        
        config = ExtractedSections().model_dump()
        
        version = config["version"]

        assert isinstance(version, str)

        self.schema_dir = os.path.join(os.path.dirname(__file__), 'schemas')
        schema_path = os.path.join(self.schema_dir, version)

        curr_schema = sorted(config["types"])
        if not os.path.exists(schema_path):
            os.makedirs(schema_path, exist_ok=True)
            with open(f"{schema_path}/schema.json", "w") as f:
                json.dump(curr_schema, f)
        else:
            with open(f"{schema_path}/schema.json", "r") as f:
                loaded_schema = json.load(f)
                   
            try:
                assert sorted(loaded_schema) == sorted(curr_schema)            
            except AssertionError:
                raise Exception(f"Schema version has changed. Loaded {loaded_schema}, expected {curr_schema}. Adjust version to new number or revert changes")
                

        self.version = version 
        self.base_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.dir = os.path.join(self.base_dir, version)
        if not os.path.exists(self.dir):
            os.makedirs(self.dir, exist_ok=True)
        
    
    def exists(self, accession_no, chunk_size):
        return os.path.exists(f"{self.dir}/{chunk_size}/{accession_no}.completed")
    
    def add(self, accession_no, chunk_size, classifications):
        dir_path = f"{self.dir}/{chunk_size}"
        os.makedirs(dir_path, exist_ok=True)
        path = f"{dir_path}/{accession_no}.jsonl"        
        with open(path, "a") as f:
            for cls in classifications:
                f.write(json.dumps(cls) + "\n")
                
    def mark_processed(self, accession_no, chunk_size):
        dir_path = f"{self.dir}/{chunk_size}"
        os.makedirs(dir_path, exist_ok=True)
        path = f"{dir_path}/{accession_no}.completed"
        open(path, 'a').close()
        
    def clear(self, accession_no, chunk_size):
        """Removes a partial .jsonl file if processing was interrupted."""
        path = f"{self.dir}/{chunk_size}/{accession_no}.jsonl"
        if os.path.exists(path):
            os.remove(path)
        
    def read_labeled_data(self, limit_filings=None):
        """
        Reads parsed JSON chunk records for the current version.
        If limit_filings is provided, it restricts the data to that many unique filings.
        """
        files = glob.glob(f"{self.dir}/**/*.jsonl", recursive=True)
        
        if limit_filings is not None:
            # Extract unique accession numbers and limit them
            accessions = list(set(os.path.basename(f).replace('.jsonl', '') for f in files))
            accessions = accessions[:limit_filings]
            # Keep only the files belonging to the selected filings
            files = [f for f in files if os.path.basename(f).replace('.jsonl', '') in accessions]
            
        records = []
        for file_path in files:
            with open(file_path, 'r') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return records

db = Db()

async def save_chunks(result, batch, accession_no, chunk_size):
    parsed = json.loads(result.text)
    classifications = parsed.get('classifications', [])
    
    for cls in classifications:
        chunk_id = cls.get("chunk_id")
        if chunk_id is not None and 0 <= chunk_id < len(batch):
            cls["text"] = batch[chunk_id]
            
    db.add(accession_no, chunk_size, classifications)