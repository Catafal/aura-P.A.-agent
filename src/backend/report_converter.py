import os
import asyncio
from pathlib import Path
from typing import List, Optional
from langchain_ollama import OllamaLLM
import shutil
import subprocess
import platform

class ReportConverter:
    """Converts markdown reports to LaTeX and PDF formats"""
    
    def __init__(self):
        """Initialize the converter with Ollama LLM"""
        self.llm = OllamaLLM(model="phi4:latest")
        self.desktop_path = self._get_desktop_path()
        
    def _get_desktop_path(self) -> Path:
        """Get the user's desktop path based on OS"""
        if platform.system() == "Windows":
            return Path(os.path.expanduser("~\\Desktop"))
        else:  # macOS and Linux
            return Path(os.path.expanduser("~/Desktop"))
    
    async def convert_md_to_latex(self, md_content: str) -> str:
        """Convert markdown content to LaTeX using Ollama"""
        try:
            prompt = f"""Convert this markdown to LaTeX. Output a complete document with all necessary packages:
\\documentclass{{article}}
\\usepackage{{geometry}}
\\usepackage{{hyperref}}
\\usepackage{{amsmath}}
\\usepackage{{verbatim}}
\\usepackage{{enumitem}}
\\usepackage{{graphicx}}
\\usepackage[utf8]{{inputenc}}
\\title{{Process Analysis Report}}
\\author{{Aura P.A.}}
\\date{{\\today}}

Rules for conversion:
1. Convert EVERY SINGLE WORD from markdown to LaTeX
2. Preserve all headings using appropriate \\section, \\subsection, etc.
3. Convert all lists to \\begin{{itemize}} or \\begin{{enumerate}}
4. Use \\textbf{{}} for bold text
5. Convert code blocks to \\begin{{verbatim}}
6. Keep all content, including JSON and analysis sections
7. Preserve all numerical values and percentages
8. Keep all bullet points and nested structures
9. Maintain document structure and hierarchy

Here's the markdown content to convert:

{md_content}

Output the complete LaTeX document with ALL content preserved."""

            response = await self.llm.agenerate([prompt])
            latex_content = response.generations[0][0].text.strip()
            
            # Ensure the content has proper document structure
            if "\\documentclass" not in latex_content:
                latex_content = f"""\\documentclass{{article}}
\\usepackage{{geometry}}
\\usepackage{{hyperref}}
\\usepackage{{amsmath}}
\\usepackage{{verbatim}}
\\usepackage{{enumitem}}
\\usepackage{{graphicx}}
\\usepackage[utf8]{{inputenc}}
\\title{{Process Analysis Report}}
\\author{{Aura P.A.}}
\\date{{\\today}}

\\begin{{document}}
\\maketitle

{latex_content}

\\end{{document}}"""
            
            return latex_content
        except Exception as e:
            print(f"Error during markdown to LaTeX conversion: {str(e)}")
            return f"""\\documentclass{{article}}
\\usepackage{{geometry}}
\\usepackage{{amsmath}}
\\usepackage{{verbatim}}
\\begin{{document}}
{md_content}
\\end{{document}}"""
    
    def _create_output_structure(self, source_dir: Path) -> Path:
        """Create output directory structure on desktop"""
        reports_dir = self.desktop_path / "process_analysis_reports"
        if source_dir.name != "reports":
            reports_dir = reports_dir / source_dir.relative_to(source_dir.parent.parent / "reports")
        
        reports_dir.mkdir(parents=True, exist_ok=True)
        return reports_dir
    
    def _compile_latex_to_pdf(self, latex_content: str, output_path: Path) -> bool:
        """Compile LaTeX content to PDF using pdflatex"""
        try:
            temp_dir = output_path.parent / "temp_latex"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            tex_file = temp_dir / f"{output_path.stem}.tex"
            tex_file.write_text(latex_content, encoding='utf-8')
            
            # Single pdflatex run with basic options
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_file.name],
                cwd=temp_dir,
                capture_output=True,
                text=True
            )
            
            pdf_file = temp_dir / f"{output_path.stem}.pdf"
            if pdf_file.exists():
                shutil.move(str(pdf_file), str(output_path.with_suffix('.pdf')))
                shutil.rmtree(temp_dir)
                return True
            
            print(f"LaTeX error: {result.stderr}")
            return False
            
        except Exception as e:
            print(f"PDF compilation error: {str(e)}")
            return False
    
    async def process_markdown_file(self, md_path: Path) -> bool:
        """Process a single markdown file"""
        try:
            # Read markdown content
            md_content = md_path.read_text(encoding='utf-8')
            
            # Convert to LaTeX
            print(f"Converting {md_path.name} to LaTeX...")
            latex_content = await self.convert_md_to_latex(md_content)
            
            # Create output directory structure
            output_dir = self._create_output_structure(md_path.parent)
            output_path = output_dir / md_path.name
            
            # Copy original markdown file
            shutil.copy2(md_path, output_path)
            print(f"Markdown file copied: {output_path}")
            
            # Save LaTeX file
            latex_path = output_path.with_suffix('.tex')
            latex_path.write_text(latex_content, encoding='utf-8')
            print(f"LaTeX file saved: {latex_path}")
            
            # Compile to PDF
            print(f"Compiling {latex_path.name} to PDF...")
            if self._compile_latex_to_pdf(latex_content, output_path):
                print(f"PDF created: {output_path.with_suffix('.pdf')}")
                return True
            else:
                print(f"Failed to create PDF for {md_path.name}")
                return False
                
        except Exception as e:
            print(f"Error processing {md_path.name}: {str(e)}")
            return False
    
    async def convert_reports(self, reports_dir: Optional[str] = None):
        """Convert all markdown reports in directory to LaTeX and PDF"""
        if reports_dir is None:
            reports_dir = "reports"
            
        reports_path = Path(reports_dir)
        if not reports_path.exists():
            raise FileNotFoundError(f"Reports directory not found: {reports_dir}")
        
        # Find all markdown files
        md_files = list(reports_path.rglob("*.md"))
        if not md_files:
            print(f"No markdown files found in {reports_dir}")
            return
        
        print(f"Found {len(md_files)} markdown files to process")
        
        # Process all files
        tasks = [self.process_markdown_file(md_file) for md_file in md_files]
        results = await asyncio.gather(*tasks)
        
        # Report results
        successful = sum(1 for r in results if r)
        print(f"\nConversion complete!")
        print(f"Successfully converted: {successful}/{len(md_files)} files")
        print(f"Reports saved to: {self.desktop_path}/process_analysis_reports")

def find_reports(base_dir="/Volumes/970Evo Plus/GitHub/aura-P.A.-agent/tests/reports"):
    """
    Find all markdown report files in the specified directory and its subdirectories.
    
    Args:
        base_dir (str): Base directory to search for reports (default: tests/reports)
        
    Returns:
        list: List of paths to markdown report files
    """
    report_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.md'):
                report_files.append(os.path.join(root, file))
    return report_files

async def process_reports():
    """Process all report files and convert them to the desired format."""
    # Find all report files
    report_files = find_reports()
    
    converter = ReportConverter()
    for report_path in report_files:
        try:
            await converter.process_markdown_file(Path(report_path))
        except Exception as e:
            print(f"Error processing {report_path}: {str(e)}")

async def main():
    """Main function to run the converter"""
    try:
        await process_reports()
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 