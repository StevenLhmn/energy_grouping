import plotly.graph_objects as go
from src.animation.trajectory import Trajectory

class Animation:
    trajectory: Trajectory = None

    def __init__(self):
        self.fig = go.Figure()

    def play(self, trajectory: Trajectory):
        if trajectory is None:
            print("no trajectory given to play")
            return
        frames = trajectory.get_frames()
        print(frames)
        self.fig = go.Figure(
            data=frames[0].data,
            frames=frames,
        )
        self._layout()
        self.fig.show()

    def _layout(self):
        self.fig.update_layout(
            updatemenus=[
                {
                    "type": "buttons",
                    "buttons": [
                        {
                            "label": "▶ Play",
                            "method": "animate",
                            "args": [
                                None,
                                {
                                    "frame": {"duration": 500},
                                    "fromcurrent": True,
                                },
                            ],
                        }
                    ],
                }
            ]
        )