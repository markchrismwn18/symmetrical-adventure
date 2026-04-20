"""
Unit tests for orbital mechanics engine
"""

import pytest
import numpy as np
from src.pp_nf_model import PPNFModel
from src.orbital_mechanics import OrbitalMechanics, OrbitalState


class TestOrbitalState:
    """Test orbital state representation"""
    
    def test_state_initialization(self):
        """Test orbital state initialization"""
        pos = np.array([1e7, 0, 0])
        vel = np.array([0, 7500, 0])
        state = OrbitalState(pos, vel, time=0.0)
        
        assert np.allclose(state.position, pos)
        assert np.allclose(state.velocity, vel)
        assert state.time == 0.0
    
    def test_distance_from_origin(self):
        """Test distance calculation"""
        pos = np.array([3e6, 4e6, 0])
        vel = np.array([0, 0, 0])
        state = OrbitalState(pos, vel)
        
        distance = state.distance_from_origin()
        expected = 5e6
        assert np.isclose(distance, expected)
    
    def test_speed(self):
        """Test speed magnitude calculation"""
        pos = np.array([0, 0, 0])
        vel = np.array([3000, 4000, 0])
        state = OrbitalState(pos, vel)
        
        speed = state.speed()
        expected = 5000
        assert np.isclose(speed, expected)


class TestOrbitalMechanics:
    """Test orbital mechanics engine"""
    
    def test_mechanics_initialization(self):
        """Test mechanics initialization"""
        mechanics = OrbitalMechanics()
        assert mechanics.model is not None
        assert mechanics.G == 6.67430e-11
    
    def test_acceleration_at_origin(self):
        """Test acceleration at origin (should be zero)"""
        mechanics = OrbitalMechanics()
        state = OrbitalState(np.array([1e-15, 0, 0]), np.array([0, 0, 0]))
        accel = mechanics.compute_acceleration(state, 5.972e24)
        
        assert np.allclose(accel, [0, 0, 0])
    
    def test_acceleration_magnitude_direction(self):
        """Test acceleration magnitude and direction"""
        mechanics = OrbitalMechanics()
        earth_mass = 5.972e24
        
        # Position at distance r
        r = 1e7
        state = OrbitalState(np.array([r, 0, 0]), np.array([0, 0, 0]))
        accel = mechanics.compute_acceleration(state, earth_mass)
        
        # Acceleration should point toward center (negative x)
        assert accel[0] < 0
        assert accel[1] == 0
        assert accel[2] == 0
    
    def test_rk4_step(self):
        """Test RK4 integration step"""
        mechanics = OrbitalMechanics()
        earth_mass = 5.972e24
        
        # Circular orbit initial conditions
        r = 6.371e6 + 400e3  # LEO altitude
        v = np.sqrt(6.67430e-11 * earth_mass / r)
        
        initial_state = OrbitalState(
            np.array([r, 0, 0]),
            np.array([0, v, 0])
        )
        
        dt = 60  # 60 second step
        new_state = mechanics.rk4_step(initial_state, dt, earth_mass)
        
        # State should advance
        assert new_state.time == dt
        assert new_state.position is not None
        assert new_state.velocity is not None
    
    def test_propagate_orbit(self):
        """Test orbital propagation"""
        mechanics = OrbitalMechanics()
        earth_mass = 5.972e24
        
        # LEO initial conditions
        r = 6.371e6 + 400e3
        v = np.sqrt(6.67430e-11 * earth_mass / r)
        
        initial_state = OrbitalState(
            np.array([r, 0, 0]),
            np.array([0, v, 0])
        )
        
        # Propagate for 1 day with 1-hour steps
        trajectory = mechanics.propagate(
            initial_state,
            duration=86400,
            central_mass=earth_mass,
            dt=3600
        )
        
        assert len(trajectory) > 1
        assert trajectory[0].time == 0.0
        assert trajectory[-1].time == 86400.0
    
    def test_orbital_elements(self):
        """Test orbital element calculation"""
        mechanics = OrbitalMechanics()
        earth_mu = 3.986004418e14
        
        # Circular orbit
        r = 6.371e6 + 400e3
        v = np.sqrt(earth_mu / r)
        
        state = OrbitalState(
            np.array([r, 0, 0]),
            np.array([0, v, 0])
        )
        
        elements = mechanics.compute_orbital_elements(state, 5.972e24)
        
        # Check semi-major axis
        assert np.isclose(elements['semi_major_axis'], r, rtol=0.01)
        
        # Check eccentricity (should be near zero for circular orbit)
        assert elements['eccentricity'] < 0.01
