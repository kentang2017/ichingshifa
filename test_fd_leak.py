import pickle
import os
import tempfile
import pytest


def test_file_descriptor_cleanup():
    """Verify file descriptor cleanup with pickle.load context manager."""
    pid = os.getpid()
    try:
        initial_fds = len(os.listdir(f'/proc/{pid}/fd'))
    except FileNotFoundError:
        # macOS doesn't have /proc; skip this test
        pytest.skip("FD counting not available on this platform")
    
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
        corrupt_path = f.name
        f.write(b'\x80\x04invalid')  # Corrupted pickle data
    
    try:
        # GOOD code: No leak with context manager
        def fixed_load(path):
            with open(path, 'rb') as f:
                return pickle.load(f)  # FIX: guaranteed cleanup
        
        # Attempt 100 times to ensure no leaks
        for i in range(100):
            try:
                fixed_load(corrupt_path)
            except (pickle.UnpicklingError, EOFError):
                pass
        
        # Check for fd leak
        final_fds = len(os.listdir(f'/proc/{pid}/fd'))
        assert final_fds == initial_fds, \
            f"FD leak: started {initial_fds}, now {final_fds} (+{final_fds - initial_fds})"
    finally:
        os.unlink(corrupt_path)


def test_pickle_successful_load():
    """Verify successful pickle load still works."""
    import tempfile
    
    # Create valid pickle file
    test_data = {'key': 'value', 'number': 42}
    
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
        pickle_path = f.name
        pickle.dump(test_data, f)
    
    try:
        # Load with context manager
        with open(pickle_path, 'rb') as f:
            loaded = pickle.load(f)
        
        assert loaded == test_data
    finally:
        os.unlink(pickle_path)
