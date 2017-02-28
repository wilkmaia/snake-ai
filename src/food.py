import game


class Food:
    def __init__(self, x=0, y=0):
        self.x = x * game.STEP
        self.y = y * game.STEP
        self.available = True

    def draw(self, surface, image):
        if self.available:
            surface.blit(image, (self.x, self.y))

    def relocate(self, x=0, y=0):
        self.x = x * game.STEP
        self.y = y * game.STEP
