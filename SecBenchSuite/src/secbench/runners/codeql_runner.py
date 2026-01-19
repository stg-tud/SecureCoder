import asyncio
import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class CodeQLRunner:
    def __init__(self, codeql_path: str = "codeql"):
        self.codeql_path = codeql_path

    async def check_available(self) -> bool:
        """Check if codeql is available."""
        return shutil.which(self.codeql_path) is not None

    async def create_database(self, source_root: Path, db_path: Path, language: str) -> bool:
        """Create CodeQL database."""
        if db_path.exists():
            shutil.rmtree(db_path)
            
        cmd = [
            self.codeql_path,
            "database",
            "create",
            str(db_path),
            f"--language={language}",
            f"--source-root={str(source_root)}",
            "--overwrite"
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"CodeQL DB creation failed: {stderr.decode()}")
            return False
        return True

    async def analyze(
        self, 
        db_path: Path, 
        output_path: Path, 
        queries: List[str] = ["codeql/python-queries:codeql-suites/python-security-extended.qls"]
    ) -> bool:
        """Run CodeQL analysis."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            self.codeql_path,
            "database",
            "analyze",
            str(db_path),
            "--format=sarif-latest",
            f"--output={str(output_path)}",
        ] + queries
        
        logger.info(f"Running CodeQL analysis: {' '.join(cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"CodeQL analysis failed: {stderr.decode()}")
            return False
        return True

    def load_sarif_results(self, sarif_path: Path) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parse SARIF and return a map of filename -> list of findings.
        Each finding contains ruleId, message, and list of CWEs tags.
        """
        if not sarif_path.exists():
            return {}
            
        with open(sarif_path, "r") as f:
            sarif = json.load(f)
            
        results_map = {}
        
        for run in sarif.get("runs", []):
            # Parse rules to map ruleId to tags (CWEs)
            rules_map = {}
            tool = run.get("tool", {}).get("driver", {})
            for rule in tool.get("rules", []):
                rule_id = rule.get("id")
                tags = rule.get("properties", {}).get("tags", [])
                cwes = [t.split("/")[-1].upper() for t in tags if "external/cwe" in t]
                rules_map[rule_id] = cwes
                
            # Parse results
            for result in run.get("results", []):
                rule_id = result.get("ruleId")
                cwes = rules_map.get(rule_id, [])
                
                locations = result.get("locations", [])
                if not locations:
                    continue
                    
                # Assuming single file analysis mostly
                # Get filename relative to source root
                # Usually uri is like file:///path/to/src/file.py or local path
                uri = locations[0].get("physicalLocation", {}).get("artifactLocation", {}).get("uri")
                if not uri:
                    continue
                
                # Normalize filename (basename)
                filename = Path(uri).name
                
                if filename not in results_map:
                    results_map[filename] = []
                    
                results_map[filename].append({
                    "rule_id": rule_id,
                    "cwes": cwes,
                    "message": result.get("message", {}).get("text", "")
                })
                
        return results_map
