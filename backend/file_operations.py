import os
import shutil
from typing import List, Dict


def get_directory_size(path: str) -> int:
    """Calculate the total size of a directory in bytes."""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, FileNotFoundError):
                    pass
    except (OSError, PermissionError):
        pass
    return total_size


def format_size(bytes_size: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def validate_path(path: str, base_path: str) -> bool:
    """Validate that the path is within the base path (prevent directory traversal)."""
    try:
        # Prevent absolute path injection by stripping leading slashes
        path = path.lstrip('/').lstrip('\\')
        full_path = os.path.abspath(os.path.join(base_path, path))
        return full_path.startswith(os.path.abspath(base_path))
    except Exception:
        return False


def list_directory(
    base_path: str, 
    relative_path: str = "", 
    limit: int = None, 
    offset: int = 0,
    sort_by: str = "modified", 
    order: str = "desc"
) -> Dict:
    """List contents of a directory with file/folder information.
    
    Args:
        base_path: The base path to list from
        relative_path: Relative path within base_path
        limit: Maximum number of items to return (for pagination)
        offset: Number of items to skip (for pagination)
        sort_by: Field to sort by ('name', 'size', 'modified')
        order: Sort order ('asc', 'desc')
    
    Returns:
        Dictionary with 'items', 'total', 'has_more' keys
    """
    # Normalize path to prevent directory traversal
    relative_path = relative_path.lstrip('/').replace('\\', '/')
    if '..' in relative_path or relative_path.startswith('/'):
        return {"items": [], "total": 0, "has_more": False}
    
    full_path = os.path.normpath(os.path.join(base_path, relative_path))
    
    # Security check: ensure we're still within base_path
    if not full_path.startswith(os.path.abspath(base_path)):
        return {"items": [], "total": 0, "has_more": False}
    
    if not os.path.exists(full_path):
        return {"items": [], "total": 0, "has_more": False}
    
    if not os.path.isdir(full_path):
        return {"items": [], "total": 0, "has_more": False}
    
    all_items = []
    
    try:
        # Use scandir for better performance (one syscall for iter + stat)
        with os.scandir(full_path) as entries:
            for entry in entries:
                try:
                    is_dir = entry.is_dir()
                    # Stat the entry to get size/mtime
                    # scandir caches stat on Windows usually, or on Linux
                    stat = entry.stat()
                    
                    size = 0
                    if not is_dir:
                        size = stat.st_size
                    
                    modified = stat.st_mtime
                    
                    # Prepare item dict (lightweight for sorting)
                    all_items.append({
                        "name": entry.name,
                        "path": os.path.join(relative_path, entry.name).replace('\\', '/'),
                        "is_directory": is_dir,
                        "size": size,
                        "size_formatted": format_size(size) if not is_dir else "—",
                        "modified": modified
                    })
                    
                except (OSError, PermissionError):
                    # Skip problematic files
                    continue
                    
        # SORTING LOGIC
        reverse = (order == "desc")
        
        def sort_key(item):
            # Directories always on top? Or mixed?
            # Standard explorer: folders first, then files.
            # Within that: sort by field.
            
            # Primary sort: Directory vs File (Folders always first)
            # 0 for dir, 1 for file
            type_score = 0 if item["is_directory"] else 1
            
            # Secondary sort: value
            val = item.get(sort_by)
            
            if sort_by == 'name':
                val = item['name'].lower()
            elif sort_by == 'modified':
                 val = item['modified']
            elif sort_by == 'size':
                 val = item['size']
            
            # If we are sorting DESC, we want larger values first.
            # But we want Folders on top regardless of ascending/descending usually?
            # Let's keep folders on top always.
            return (type_score, val if not reverse else -val if isinstance(val, (int, float)) else val)

        # Better Sort Strategy:
        # Separately sort folders and files, then merge?
        # Or just use a complex key.
        
        # Simple Logic:
        # 1. Separate Folders and Files
        folders = [x for x in all_items if x["is_directory"]]
        files = [x for x in all_items if not x["is_directory"]]
        
        # 2. Sort each group
        if sort_by == 'name':
             if reverse:
                 folders.sort(key=lambda x: x['name'].lower(), reverse=True)
                 files.sort(key=lambda x: x['name'].lower(), reverse=True)
             else:
                 folders.sort(key=lambda x: x['name'].lower())
                 files.sort(key=lambda x: x['name'].lower())
                 
        elif sort_by == 'modified':
             # Date: Defaults to DESC usually
             folders.sort(key=lambda x: x['modified'], reverse=reverse)
             files.sort(key=lambda x: x['modified'], reverse=reverse)
             
        elif sort_by == 'size':
             folders.sort(key=lambda x: x['size'], reverse=reverse)
             files.sort(key=lambda x: x['size'], reverse=reverse)
        
        # 3. Merge (Folders always first)
        all_items_sorted = folders + files
        
        total_count = len(all_items_sorted)
        
        # Apply pagination
        if limit is not None:
            result_items = all_items_sorted[offset:offset + limit]
        else:
            result_items = all_items_sorted[offset:]
            
    except PermissionError:
        result_items = []
        total_count = 0
    
    has_more = limit is not None and (offset + limit) < total_count
    
    result = {
        "items": result_items,
        "total": total_count,
        "has_more": has_more
    }
    
    return result


def get_folder_info(base_path: str, relative_path: str, calculate_size: bool = False) -> Dict:
    """Get detailed information about a specific folder.
    
    Args:
        base_path: The base path
        relative_path: Relative path within base_path
        calculate_size: If True, calculate full recursive size (slow for large folders)
    """
    # Normalize path to prevent directory traversal
    relative_path = relative_path.lstrip('/').replace('\\', '/')
    if '..' in relative_path or relative_path.startswith('/'):
        return None
    
    full_path = os.path.normpath(os.path.join(base_path, relative_path))
    
    # Security check: ensure we're still within base_path
    if not full_path.startswith(os.path.abspath(base_path)):
        return None
    
    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        return None
    
    # Get item count (fast)
    try:
        item_count = len(os.listdir(full_path))
    except (OSError, PermissionError):
        item_count = 0
    
    # Only calculate size if explicitly requested (slow for large folders)
    if calculate_size:
        size = get_directory_size(full_path)
        size_formatted = format_size(size)
    else:
        size = 0
        size_formatted = f"{item_count} items"
    
    return {
        "path": relative_path,
        "size": size,
        "size_formatted": size_formatted,
        "exists": True,
        "item_count": item_count
    }


def delete_path(base_path: str, relative_path: str) -> bool:
    """Delete a file or directory recursively.
    
    Args:
        base_path: The base path
        relative_path: Relative path within base_path
    """
    # Normalize path to prevent directory traversal
    relative_path = relative_path.lstrip('/').replace('\\', '/')
    if '..' in relative_path or relative_path.startswith('/'):
        raise ValueError("Invalid path")
    
    full_path = os.path.normpath(os.path.join(base_path, relative_path))
    
    # Security check: ensure we're still within base_path
    if not full_path.startswith(os.path.abspath(base_path)):
        raise ValueError("Path is outside base directory")
    
    if not os.path.exists(full_path):
        raise FileNotFoundError("Path not found")
        
    try:
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        return True
    except Exception as e:
        raise OSError(f"Failed to delete path: {str(e)}")
