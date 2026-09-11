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
        elif not isinstance(trajectory, Trajectory):
            print(f'no trajectory given to play, type was {type(trajectory)}')
            return
        elif trajectory.get_frames() == []:
            print(f'trajectory was empty')
            return
        frames = trajectory.get_frames()
        for frame in frames:
            frame.layout = go.Layout(title_text=str(frame.name))
        self.fig = go.Figure(
            data=frames[0].data,
            frames=frames,
        )
        self._layout()
        self.fig.update_layout(title_text=str(frames[0].name))
        self.fig.show()

    def _layout(self):
        frames = list(self.fig.frames)
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
                                    "frame": {"duration": 1000, "redraw": True},
                                    "transition": {"duration": 0},
                                    "fromcurrent": True,
                                },
                            ],
                        }
                    ],
                }
            ],
            sliders=[
                {
                    "active": 0,
                    "currentvalue": {"prefix": "Frame: "},
                    "steps": [
                        {
                            "label": str(frame.name),
                            "method": "animate",
                            "args": [
                                [frame.name],
                                {
                                    "frame": {"duration": 0, "redraw": True},
                                    "transition": {"duration": 0},
                                    "mode": "immediate",
                                },
                            ],
                        }
                        for frame in frames
                    ],
                }
            ],
        )
