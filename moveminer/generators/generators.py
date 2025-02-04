from typing import Callable, Optional, Tuple
from ..core.Trajectory import Trajectory
import pandas as pd
import numpy as np
import abc


class Generator(metaclass=abc.ABCMeta):
    """Abstract base class for trajectory generators."""

    def __init__(
        self,
        T: float,
        dim: int = 2,
        N: int = 1,
        dt: float = 1.0,
        seed: Optional[int] = None,
    ):
        """Initialize the generator with simulation parameters."""
        self.T = T  # Total time
        self.dim = dim  # Trajectory dimension
        self.N = N  # Number of trajectories
        self.dt = dt  # Time step of the simulation
        self.n = int(T / dt)  # Number of time steps
        self.rng = (
            np.random.default_rng(seed) if seed is not None else np.random.default_rng()
        )

    @abc.abstractmethod
    def generate(self):
        """Abstract method to generate trajectories."""
        pass


class RandomWalkGenerator(Generator):
    """Class for generating random walk trajectories."""

    def __init__(
        self,
        T: float,
        dim: int = 2,
        N: int = 1,
        dt: float = 1.0,
        actions_prob: Optional[np.ndarray] = None,
        step_length_func: Callable[[Tuple], np.ndarray] = np.ones,
        seed: Optional[int] = None,
        **step_length_kwargs,
    ):
        super().__init__(T, dim, N, dt, seed)

        self.t = np.arange(self.n) * dt  # Time array
        self.r = np.zeros((self.n, dim, N))  # Position array

        # Model parameters
        actions = np.array([-1, 0, 1])
        actions_prob = (
            np.tile([1 / 3, 1 / 3, 1 / 3], (dim, 1))
            if actions_prob is None
            else np.asarray(actions_prob, dtype=np.float32)
        )

        if actions_prob.shape != (dim, len(actions)):
            raise ValueError(
                f"actions_prob must have shape like (dims, {len(actions)})"
            )

        shape_tuple = (self.n - 1, dim, N)
        self.actions = actions
        self.actions_prob = actions_prob
        self.step_length = step_length_func(shape_tuple, **step_length_kwargs)

    def _get_position_vectors(self):
        """Compute vector position as a function of time for all the walkers of the ensemble."""
        # Get displacement for every coordinates according to the probabilities in self.actions_prob
        delta_r = [
            self.rng.choice(self.actions, p=p, size=(self.n - 1, self.N))
            for p in self.actions_prob
        ]
        delta_r = np.swapaxes(
            delta_r, 0, 1
        )  # Set time/coordinates as the first/second axis
        delta_r = (
            delta_r * self.step_length
        )  # Scale displacements according to the jump length statistics
        self.r[1:] = np.cumsum(
            delta_r, axis=0
        )  # Integrate displacements to get position vectors
        return self.r

    def generate(self):
        """Get position vectors and generate RandomWalk object."""
        r = self._get_position_vectors()  # Get position vectors
        # trajs = [r[:, :, i] for i in range(self.N)]
        trajs = []
        # Generate RandomWalk object
        for i in range(self.N):
            points = r[:, :, i]
            df = pd.DataFrame(
                {
                    "id": f"RandomWald_{i}",
                    "x": points[:, 0],
                    "y": points[:, 1],
                    "t": self.t,
                }
            )
            traj = Trajectory(df, x="x", y="y", t="t")
            trajs.append(traj)
        return trajs
