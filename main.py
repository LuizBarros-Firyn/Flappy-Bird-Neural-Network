import pygame
import os
import random
import neat

is_ai_playing = True
generation = 0

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800

PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
GROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
BIRD_IMAGES = [
  pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
  pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
  pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))),
]

pygame.font.init()

SCORE_FONT = pygame.font.SysFont('arial', 50)

class Bird:
  IMGS = BIRD_IMAGES
  MAXIMUM_ROTATION = 25
  ROTATION_SPEED = 20
  ANIMATION_TIME = 5

  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.angle = 0
    self.speed = 0
    self.height = self.y
    self.time = 0
    self.image_count = 0
    self.image = self.IMGS[0]

  def jump(self):
    self.speed = - 10.5
    self.time = 0
    self.height = self.y

  def move(self):
    self.time += 1

    movement = 1.5 * (self.time**2) + self.speed * self.time

    if movement > 16:
      movement = 16
    elif movement < 0:
      movement -= 2

    self.y += movement

    if movement < 0 or self.y < (self.height + 50):
        if self.angle < self.MAXIMUM_ROTATION:
            self.angle = self.MAXIMUM_ROTATION
    else:
        if self.angle > -90:
            self.angle -= self.ROTATION_SPEED

  def draw(self, screen):
    self.image_count += 1

    if self.image_count < self.ANIMATION_TIME:
      self.image = self.IMGS[0]
    elif self.image_count < self.ANIMATION_TIME * 2:
      self.image = self.IMGS[1]
    elif self.image_count < self.ANIMATION_TIME * 3:
      self.image = self.IMGS[2]
    elif self.image_count < self.ANIMATION_TIME * 4:
      self.image = self.IMGS[1]
    elif self.image_count < self.ANIMATION_TIME * 4 + 1:
      self.image = self.IMGS[0]
      self.image_count = 0

    if self.angle <= -80:
      self.image = self.IMGS[1]
      self.image_count = self.ANIMATION_TIME * 2

    rotationed_image = pygame.transform.rotate(self.image, self.angle)
    image_center_position = self.image.get_rect(topleft=(self.x, self.y)).center
    rectangle = rotationed_image.get_rect(center=image_center_position)
    screen.blit(rotationed_image, rectangle.topleft)

  def get_mask(self):
    return pygame.mask.from_surface(self.image)

class Pipe:
  DISTANCE = 200
  SPEED = 5

  def __init__(self, x):
    self.x = x
    self.height = 0
    self.top_position = 0
    self.bottom_position = 0
    self.TOP_PIPE = pygame.transform.flip(PIPE_IMAGE, False, True)
    self.BOTTOM_PIPE = PIPE_IMAGE
    self.has_passed = False
    self.define_height()

  def define_height(self):
    self.height = random.randrange(0, 500)
    self.top_position = self.height - self.TOP_PIPE.get_height()
    self.bottom_position = self.height + self.DISTANCE

  def move(self):
    self.x -= self.SPEED

  def draw(self, screen):
    screen.blit(self.TOP_PIPE, (self.x, self.top_position))
    screen.blit(self.BOTTOM_PIPE, (self.x, self.bottom_position))

  def colide(self, bird):
    bird_mask = bird.get_mask()
    top_mask = pygame.mask.from_surface(self.TOP_PIPE)
    bottom_mask = pygame.mask.from_surface(self.BOTTOM_PIPE)

    top_distance = (self.x - bird.x, self.top_position - round(bird.y))
    bottom_distance = (self.x - bird.x, self.bottom_position  - round(bird.y))

    top_colision = bird_mask.overlap(top_mask, top_distance)
    bottom_colision = bird_mask.overlap(bottom_mask, bottom_distance)

    if top_colision or bottom_colision:
      return True
    else:
      return False


class Ground:
  SPEED = 5
  WIDTH = GROUND_IMAGE.get_width()
  IMAGE = GROUND_IMAGE

  def __init__(self, y):
    self.y = y
    self.x1 = 0
    self.x2 = self.WIDTH

  def move(self):
    self.x1 -= self.SPEED
    self.x2 -= self.SPEED

    if self.x1 + self.WIDTH < 0:
      self.x1 = self.x2 + self.WIDTH

    if self.x2 + self.WIDTH < 0:
      self.x2 = self.x1 + self.WIDTH

  def draw(self, screen):
    screen.blit(self.IMAGE, (self.x1, self.y))
    screen.blit(self.IMAGE, (self.x2, self.y))

def draw_screen(screen, birds, pipes, ground, score):
  screen.blit(BACKGROUND_IMAGE, (0, 0))

  for bird in birds:
    bird.draw(screen)

  for pipe in pipes:
    pipe.draw(screen)

  scoreText = SCORE_FONT.render(f'Pontuação: {score}', 1, (255, 255, 255))

  screen.blit(scoreText, (SCREEN_WIDTH - 10 - scoreText.get_width(), 10))

  if is_ai_playing:
    text = SCORE_FONT.render(f'Geração: {generation}', 1, (255, 255, 255))

    screen.blit(text, (SCREEN_WIDTH - 10 - scoreText.get_width(), 70))

    alive_birds_text = SCORE_FONT.render(f'Vivos: {len(birds)}', 1, (255, 255, 255))

    screen.blit(alive_birds_text, (SCREEN_WIDTH - 10 - scoreText.get_width(), 130))


  ground.draw(screen)

  pygame.display.update()

def main(genomes, config):
  global generation
  generation += 1

  if is_ai_playing:
      networks = []
      genomes_list = []
      birds = []

      for _, genome in genomes:
        network = neat.nn.FeedForwardNetwork.create(genome, config)
        networks.append(network)
        genome.fitness = 0
        genomes_list.append(genome)
        birds.append(Bird(230, 350))

  else:
    birds = [Bird(230, 350)]

  ground = Ground(730)
  pipes = [Pipe(700)]

  screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
  score = 0
  clock = pygame.time.Clock()

  is_running = True

  while is_running:
    clock.tick(30)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        is_running = False
        pygame.quit()
        quit()

      if not is_ai_playing:
        if event.type == pygame.KEYDOWN:
          if event.key  == pygame.K_SPACE:
            for bird in birds:
              bird.jump()

    pipe_index = 0
    if (len(birds)) > 0:
      if len(pipes) > 1 and birds[0].x > (pipes[0].x + pipes[0].TOP_PIPE.get_width()):
        pipe_index = 1
    else:
      is_running = False
      break

    for i, bird in enumerate(birds):
      bird.move()

      if is_ai_playing:
        genomes_list[i].fitness += 0.1
        output = networks[i].activate((bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom_position)))

        if output[0] > 0.5:
          bird.jump()

    ground.move()

    should_add_pipe = False

    deleting_pipes = []

    for pipe in pipes:
      for i, bird in enumerate(birds):
        if pipe.colide(bird):
          birds.pop(i)
          if is_ai_playing:
            genomes_list[i].fitness -= 1
            genomes_list.pop(i)
            networks.pop(i)

        if not pipe.has_passed and bird.x > pipe.x:
          pipe.has_passed = True
          should_add_pipe = True

      pipe.move()

      if (pipe.x + pipe.TOP_PIPE.get_width() < 0):
        deleting_pipes.append(pipe)

    if should_add_pipe:
      score += 1
      pipes.append(Pipe(600))

      if is_ai_playing:
        for genome in genomes_list:
          genome.fitness += 5

    for pipe in deleting_pipes:
      pipes.remove(pipe)

    for i, bird in enumerate(birds):
      if (bird.y + bird.image.get_height()) > ground.y or bird.y < 0:
        genomes_list[i].fitness -= 5
        birds.pop(i)

        if is_ai_playing:
          genomes_list.pop(i)
          networks.pop(i)

    draw_screen(screen, birds, pipes, ground, score)

def run(config_path):
  config = neat.Config(
    neat.DefaultGenome,
    neat.DefaultReproduction,
    neat.DefaultSpeciesSet,
    neat.DefaultStagnation,
    config_path
  )

  population = neat.Population(config)
  population.add_reporter(neat.StdOutReporter(True))
  population.add_reporter(neat.StatisticsReporter())

  if is_ai_playing:
    population.run(main, 50)
  else:
    main(None, None)

if __name__ == '__main__':
  path = os.path.dirname(__file__)
  config_path = os.path.join(path, 'config.txt')

  run(config_path)