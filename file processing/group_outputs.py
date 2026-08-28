from pathlib import Path
import shutil

# This is a script written by Claude that just does some file management before processing

def copy_outputs(category: str) -> None:
	"""Copy all files in output/<category>/* (including subfolders) to "1. Unmodified Output"/<category>."""
	file_processing_dir = Path(__file__).resolve().parent
	project_root = file_processing_dir.parent
	source_dir = project_root / "output" / category
	destination_dir = file_processing_dir / "1. Unmodified Output" / category

	destination_dir.mkdir(parents=True, exist_ok=True)

	for source_path in source_dir.rglob("*"):
		if source_path.is_file() and source_path.suffix.lower() == ".wav":
			destination_path = destination_dir / source_path.name
			if destination_path.exists() and not destination_path.samefile(source_path):
				raise FileExistsError(
					f"Filename collision copying to flat folder: {destination_path} "
					f"(from {source_path})"
				)
			shutil.copy2(source_path, destination_path)


copy_outputs("GA")
copy_outputs("Southern")
