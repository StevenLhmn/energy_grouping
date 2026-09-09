import plotly.graph_objects as go


class Trajectory:
    def __init__(self):
        self.frames = []

    def _check_frame(self, frame):
        if not isinstance(frame, go.Frame):
            raise TypeError(f"frame must be a plotly.graph_objects.Frame. But was {type(frame)}")
        if frame.name is None or str(frame.name).strip() == "":
            raise ValueError("frame must have a non-empty name")
        return frame

    def log(self, frame):
        self.frames.append(self._check_frame(frame))
        
    def get_frames(self):
        return list(self.frames)