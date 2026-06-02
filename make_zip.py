import zipfile
import os

zip_name = 'freeconvert-production-package.zip'
if os.path.exists(zip_name):
    os.remove(zip_name)

exclude_dirs = {'.git', '__pycache__'}
exclude_files = {
    'freeconvert-production-package.zip', 
    'freeconvert-deploy.zip',
}
exclude_extensions = {'.py', '.md', '.txt'} # exclude python build scripts and markdown docs

count = 0
with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk('.'):
        # Exclude directories in-place to prevent walking them
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file in exclude_files:
                continue
            ext = os.path.splitext(file)[1].lower()
            if ext in exclude_extensions:
                # Keep .htaccess even if it's text (though it has no extension, splitext leaves it as '')
                if file != '.htaccess':
                    continue
            
            fp = os.path.join(root, file)
            arcname = os.path.relpath(fp, '.')
            zipf.write(fp, arcname)
            count += 1

print(f"Created zip package with {count} files.")
