import os
import hashlib
import pickle
import json

class VCS:
    def __init__(self):
        self.storage_dir = '.vcs_storage'
        self.mapping_file = os.path.join(self.storage_dir, 'hash_mapping.json')
        self.counter_file = os.path.join(self.storage_dir, 'counter.txt')
        
    def init_vcs(self):
        """Initialize the VCS system"""
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize mapping file if it doesn't exist
        if not os.path.exists(self.mapping_file):
            with open(self.mapping_file, 'w') as f:
                json.dump({}, f)
        
        # Initialize counter file if it doesn't exist
        if not os.path.exists(self.counter_file):
            with open(self.counter_file, 'w') as f:
                f.write('100000')  # Start from 100000 to ensure 6 digits
                
        print("VCS initialized.")
    
    def _get_next_short_hash(self):
        """Generate the next 6-digit hash"""
        with open(self.counter_file, 'r') as f:
            counter = int(f.read().strip())
        
        # Use the counter as base and add some randomization for uniqueness
        short_hash = f"{counter:06d}"
        
        # Increment counter for next use
        with open(self.counter_file, 'w') as f:
            f.write(str(counter + 1))
            
        return short_hash
    
    def _load_mapping(self):
        """Load the hash mapping from file"""
        try:
            with open(self.mapping_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_mapping(self, mapping):
        """Save the hash mapping to file"""
        with open(self.mapping_file, 'w') as f:
            json.dump(mapping, f, indent=2)
    
    def _get_full_hash_from_short(self, short_hash):
        """Get the full hash from a short hash"""
        mapping = self._load_mapping()
        return mapping.get(short_hash)
    
    def snapshot(self, directory='.'):
        """Create a snapshot of the directory"""
        # Calculate the full hash (original method)
        snapshot_hash = hashlib.sha256()
        snapshot_data = {'files': {}}

        for root, dirs, files in os.walk(directory):
            for file in files:
                if self.storage_dir in root or '.git' in root:
                    continue
                    
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        snapshot_hash.update(content)
                        snapshot_data['files'][file_path] = content
                except (PermissionError, FileNotFoundError):
                    print(f"Warning: Could not read {file_path}")
                    continue

        full_hash = snapshot_hash.hexdigest()
        snapshot_data['file_list'] = list(snapshot_data['files'].keys())
        
        # Generate short hash
        short_hash = self._get_next_short_hash()
        
        # Update mapping
        mapping = self._load_mapping()
        mapping[short_hash] = full_hash
        self._save_mapping(mapping)
        
        # Save snapshot with full hash as filename (for integrity)
        snapshot_path = os.path.join(self.storage_dir, full_hash)
        with open(snapshot_path, 'wb') as f:
            pickle.dump(snapshot_data, f)

        print(f"Snapshot created with hash: {short_hash}")
        print(f"Files captured: {len(snapshot_data['files'])}")
        return short_hash
    
    def revert_to_snapshot(self, short_hash):
        """Revert to a specific snapshot using short hash"""
        # Get the full hash from short hash
        full_hash = self._get_full_hash_from_short(short_hash)
        
        if not full_hash:
            print(f"Snapshot with hash {short_hash} does not exist.")
            return False
            
        snapshot_path = os.path.join(self.storage_dir, full_hash)
        
        if not os.path.exists(snapshot_path):
            print(f"Snapshot file not found for hash {short_hash}")
            return False

        try:
            with open(snapshot_path, 'rb') as f:
                snapshot_data = pickle.load(f)
        except (pickle.PickleError, FileNotFoundError):
            print(f"Error loading snapshot {short_hash}")
            return False

        # Restore files from snapshot
        for file_path, content in snapshot_data['files'].items():
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'wb') as f:
                    f.write(content)
            except (PermissionError, OSError) as e:
                print(f"Error restoring {file_path}: {e}")

        # Remove files not in snapshot
        current_files = set()
        for root, dirs, files in os.walk('.', topdown=True):
            if self.storage_dir in root or '.git' in root:
                continue
            for file in files:
                current_files.add(os.path.join(root, file))

        snapshot_files = set(snapshot_data['file_list'])
        files_to_delete = current_files - snapshot_files

        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                print(f"Removed {file_path}")
            except (PermissionError, FileNotFoundError):
                print(f"Could not remove {file_path}")

        print(f"Reverted to snapshot {short_hash}")
        return True
    
    def list_snapshots(self):
        """List all available snapshots"""
        mapping = self._load_mapping()
        
        if not mapping:
            print("No snapshots found.")
            return
            
        print("Available snapshots:")
        print("-" * 50)
        
        for short_hash, full_hash in mapping.items():
            snapshot_path = os.path.join(self.storage_dir, full_hash)
            if os.path.exists(snapshot_path):
                # Get file modification time for snapshot creation time
                creation_time = os.path.getmtime(snapshot_path)
                import datetime
                creation_date = datetime.datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
                
                # Get number of files in snapshot
                try:
                    with open(snapshot_path, 'rb') as f:
                        snapshot_data = pickle.load(f)
                        file_count = len(snapshot_data['files'])
                except:
                    file_count = "Unknown"
                
                print(f"Hash: {short_hash} | Created: {creation_date} | Files: {file_count}")
    
    def delete_snapshot(self, short_hash):
        """Delete a specific snapshot"""
        mapping = self._load_mapping()
        full_hash = mapping.get(short_hash)
        
        if not full_hash:
            print(f"Snapshot {short_hash} not found.")
            return False
            
        snapshot_path = os.path.join(self.storage_dir, full_hash)
        
        try:
            if os.path.exists(snapshot_path):
                os.remove(snapshot_path)
            
            # Remove from mapping
            del mapping[short_hash]
            self._save_mapping(mapping)
            
            print(f"Snapshot {short_hash} deleted successfully.")
            return True
            
        except (PermissionError, OSError) as e:
            print(f"Error deleting snapshot {short_hash}: {e}")
            return False

# Convenience functions for backward compatibility
def init_vcs():
    vcs = VCS()
    vcs.init_vcs()

def snapshot(directory='.'):
    vcs = VCS()
    return vcs.snapshot(directory)

def revert_to_snapshot(short_hash):
    vcs = VCS()
    return vcs.revert_to_snapshot(short_hash)

def list_snapshots():
    vcs = VCS()
    vcs.list_snapshots()

def delete_snapshot(short_hash):
    vcs = VCS()
    return vcs.delete_snapshot(short_hash)

# Example usage
if __name__ == "__main__":
    # Initialize VCS
    init_vcs()
    
    # Create a snapshot
    print("Creating snapshot...")
    short_hash = snapshot('.')
    
    # List snapshots
    print("\nListing snapshots:")
    list_snapshots()
    
    # Example of reverting (commented out to avoid actual revert)
    # print(f"\nReverting to snapshot {short_hash}...")
    # revert_to_snapshot(short_hash)
