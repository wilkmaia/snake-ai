class Food:
    x = 0
    y = 0
    STEP = 24

    def __init__(self, step, x=0, y=0):
        self.x = x * self.STEP
        self.y = y * self.STEP
        self.step = step

    def draw(self, surface, image):
        surface.blit(image, (self.x, self.y))

    def rellocate(self, x=0, y=0):
        self.x = x * self.STEP
        self.y = y * self.STEP
