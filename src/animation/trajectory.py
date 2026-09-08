class Trajectory:
    def __init__(self):
        self.frames = []

    def _check_frame(self, frame):
        return frame # TODO add stuff

    def log(self, frame):
        self.frames.append(self._check_frame(frame))
        
    def get_frames(self):
        return self.frames