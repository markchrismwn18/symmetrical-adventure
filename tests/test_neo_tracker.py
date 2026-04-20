"""
Unit tests for NEO Tracker application
"""

import pytest
import numpy as np
from src.neo_tracker import NEOTracker, NEOObject


class TestNEOObject:
    """Test NEO object representation"""
    
    def test_neo_initialization(self):
        """Test NEO initialization"""
        pos = np.array([1e7, 0, 0])
        vel = np.array([0, 7000, 0])
        neo = NEOObject('2024-AB1', 'Test Asteroid', pos, vel)
        
        assert neo.neo_id == '2024-AB1'
        assert neo.name == 'Test Asteroid'
        assert len(neo.trajectory) == 1
    
    def test_neo_add_observation(self):
        """Test adding observations to NEO"""
        pos = np.array([1e7, 0, 0])
        vel = np.array([0, 7000, 0])
        neo = NEOObject('2024-AB1', 'Test Asteroid', pos, vel)
        
        new_pos = np.array([1.01e7, 0, 0])
        new_vel = np.array([0, 7000, 0])
        neo.add_observation(new_pos, new_vel, 3600)
        
        assert len(neo.trajectory) == 2


class TestNEOTracker:
    """Test NEO Tracker application"""
    
    def test_tracker_initialization(self):
        """Test tracker initialization"""
        tracker = NEOTracker()
        
        assert tracker.model is not None
        assert tracker.mechanics is not None
        assert len(tracker.neo_catalog) == 0
        assert tracker.total_predictions == 0
    
    def test_register_neo(self):
        """Test NEO registration"""
        tracker = NEOTracker()
        pos = np.array([1e7, 0, 0])
        vel = np.array([0, 7000, 0])
        neo = NEOObject('2024-AB1', 'Test Asteroid', pos, vel)
        
        success = tracker.register_neo(neo)
        assert success is True
        assert '2024-AB1' in tracker.neo_catalog
        
        # Duplicate registration should fail
        success2 = tracker.register_neo(neo)
        assert success2 is False
    
    def test_predict_trajectory(self):
        """Test trajectory prediction"""
        tracker = NEOTracker()
        
        # Register a NEO in LEO-like orbit
        r = 6.371e6 + 400e3
        v = np.sqrt(3.986004418e14 / r)
        pos = np.array([r, 0, 0])
        vel = np.array([0, v, 0])
        neo = NEOObject('2024-AB1', 'Test Asteroid', pos, vel)
        
        tracker.register_neo(neo)
        
        # Predict trajectory
        trajectory = tracker.predict_trajectory('2024-AB1', duration_days=1, dt_seconds=3600)
        
        assert len(trajectory) > 1
        assert tracker.total_predictions == 1
    
    def test_predict_nonexistent_neo(self):
        """Test prediction of non-existent NEO raises error"""
        tracker = NEOTracker()
        
        with pytest.raises(ValueError):
            tracker.predict_trajectory('NONEXISTENT', duration_days=1)
    
    def test_close_approach_detection(self):
        """Test close approach detection"""
        tracker = NEOTracker()
        
        # Create NEO that will pass close to Earth
        pos = np.array([6.371e6 + 1e6, 0, 0])
        vel = np.array([0, 3000, 0])
        neo = NEOObject('2024-AB1', 'Dangerous Asteroid', pos, vel)
        
        tracker.register_neo(neo)
        trajectory = tracker.predict_trajectory('2024-AB1', duration_days=1, dt_seconds=3600)
        
        approach = tracker.check_close_approach('2024-AB1', trajectory, threshold_km=10e6)
        
        assert 'neo_id' in approach
        assert 'closest_approach_km' in approach
        assert 'risk_level' in approach
    
    def test_batch_predict(self):
        """Test batch prediction for all NEOs"""
        tracker = NEOTracker()
        
        # Register multiple NEOs
        for i in range(3):
            r = 6.371e6 + 400e3
            v = np.sqrt(3.986004418e14 / r)
            pos = np.array([r, 0, 0])
            vel = np.array([0, v, 0])
            neo = NEOObject(f'NEO-{i}', f'Asteroid {i}', pos, vel)
            tracker.register_neo(neo)
        
        results = tracker.batch_predict(duration_days=1)
        
        assert len(results) == 3
        assert all(neo_id in results for neo_id in ['NEO-0', 'NEO-1', 'NEO-2'])
    
    def test_catalog_stats(self):
        """Test catalog statistics"""
        tracker = NEOTracker()
        
        # Register some NEOs
        for i in range(2):
            r = 6.371e6 + 400e3
            v = np.sqrt(3.986004418e14 / r)
            pos = np.array([r, 0, 0])
            vel = np.array([0, v, 0])
            neo = NEOObject(f'NEO-{i}', f'Asteroid {i}', pos, vel)
            tracker.register_neo(neo)
        
        stats = tracker.get_catalog_stats()
        
        assert stats['total_tracked'] == 2
        assert 'model_version' in stats
    
    def test_export_report(self):
        """Test report generation"""
        tracker = NEOTracker()
        
        report = tracker.export_report()
        
        assert 'PP-NF NEO TRACKING REPORT' in report
        assert 'MODEL CONFIGURATION' in report
        assert 'TRACKING STATISTICS' in report
