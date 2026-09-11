import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
from IPython.display import clear_output, display
from src.animation.trajectory import Trajectory

class Animation:
    trajectory: Trajectory = None

    def __init__(self):
        self.fig = go.Figure()
        self.trajectory = Trajectory()
        self._scores = []

    def receive(self, frame: go.Frame, show: bool = True):
        """Log and optionally display the current frame immediately."""
        self.trajectory.log(frame)
        score = self._frame_score(frame)
        if score is not None:
            self._scores.append(score)
        self.fig = self._make_figure(
            frame,
            self._scores,
            self._coordinate_ranges([frame]),
            len(self._scores),
        )
        if show:
            self._display()

    def play(self, trajectory: Trajectory = None, speed: int = 500):
        """Replay a trajectory, or the frames received by this animation."""
        if trajectory is None:
            trajectory = self.trajectory
        if not isinstance(trajectory, Trajectory):
            print(f'no trajectory given to play, type was {type(trajectory)}')
            return
        elif trajectory.get_frames() == []:
            print(f'trajectory was empty')
            return
        frames = trajectory.get_frames()
        scores = [self._frame_score(frame) for frame in frames]
        scores = [score for score in scores if score is not None]
        self.fig = self._make_figure(
            frames[0],
            scores[:1],
            self._coordinate_ranges(frames),
            len(scores),
        )
        animation_frames = []
        for index, frame in enumerate(frames):
            frame_scores = scores[:index + 1]
            curve = self._learning_curve(frame_scores)
            frame_data = [self._map_trace(trace) for trace in frame.data]
            frame_data.append(curve)
            animation_frames.append(go.Frame(
                name=str(frame.name),
                data=frame_data,
                layout=frame.layout,
            ))
        self.fig.frames = animation_frames
        self._layout(speed=speed)
        self._display()

    def _display(self):
        clear_output(wait=True)
        display(self.fig)

    @staticmethod
    def _frame_score(frame):
        """Return the numeric score stored on a frame, if present."""
        frame_layout = frame.layout
        if frame_layout is not None and isinstance(frame_layout.meta, dict):
            score = frame_layout.meta.get("score")
            return float(score) if score is not None else None
        return None

    @staticmethod
    def _map_trace(trace):
        trace.update(xaxis="x", yaxis="y")
        return trace

    @staticmethod
    def _learning_curve(scores):
        curve = go.Scatter(
            x=list(range(len(scores))),
            y=scores,
            mode="lines+markers",
            name="Best score",
            line=dict(color="#222222"),
        )
        curve.update(xaxis="x2", yaxis="y2")
        return curve

    @staticmethod
    def _coordinate_ranges(frames):
        x_coordinates = []
        y_coordinates = []
        for frame in frames:
            for trace in frame.data:
                x_values = [] if trace.x is None else trace.x
                y_values = [] if trace.y is None else trace.y
                x_coordinates.extend(x_values)
                y_coordinates.extend(y_values)

        def padded_range(coordinates):
            values = np.asarray(coordinates, dtype=float)
            if values.size == 0:
                return [-1, 1]
            lower = float(np.nanmin(values))
            upper = float(np.nanmax(values))
            span = max(upper - lower, 1.0)
            padding = span * 0.05
            return [lower - padding, upper + padding]

        return padded_range(x_coordinates), padded_range(y_coordinates)

    def _make_figure(self, frame, scores, coordinate_ranges, iteration_count):
        figure = make_subplots(
            rows=1,
            cols=2,
            column_widths=[0.58, 0.42],
            subplot_titles=("Grouping", "Learning curve"),
        )
        for trace in frame.data:
            figure.add_trace(trace, row=1, col=1)
        if scores:
            figure.add_trace(self._learning_curve(scores), row=1, col=2)
        x_range, y_range = coordinate_ranges
        figure.update_xaxes(
            title_text="x",
            range=x_range,
            row=1,
            col=1,
        )
        figure.update_yaxes(
            title_text="y",
            range=y_range,
            scaleanchor="x",
            scaleratio=1,
            constrain="domain",
            row=1,
            col=1,
        )
        figure.update_xaxes(
            title_text="Iteration",
            range=[0, max(iteration_count - 1, 1)],
            row=1,
            col=2,
        )
        figure.update_yaxes(
            title_text="Score",
            range=[0, 1],
            row=1,
            col=2,
        )
        figure.update_layout(title_text=str(frame.layout.title.text if frame.layout and frame.layout.title else frame.name))
        return figure

    def _layout(self, speed: int):
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
                                    "frame": {"duration": speed, "redraw": True},
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
