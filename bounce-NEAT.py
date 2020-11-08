import pygame
import neat
import time
import os
import random
import math
pygame.font.init()

GEN=0
WIN_WIDTH = 800
WIN_HEIGHT = 600
BALL_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "ball.png")))
BG_IMG = pygame.image.load(os.path.join("imgs", "BG.png"))
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe1.png")))
#STAT_FONT = pygame.font.SysFont("GOTHIC.tff", 35)
STAT_FONT = pygame.font.Font("Roboto-Light.ttf", 30)

class Ball:
	IMGS = BALL_IMG
	VEL = 5

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.tick_count = 0
		self.vel =0
		self.height = self.y   
		self.img = self.IMGS
		self.touch_pipe = 1
		self.height_limit = 0
		self.test = 0

	def jump(self):
		#if condition to check for base
		#self.touch_pipe = 0
		self.vel = -10  
		self.tick_count = 0
		self.height = self.y

		if self.height <= 50:
			self.height_limit = 1
			self.test = 1
			#self.touch_pipe = 0                   
			
		if self.test == 1:
			if self.height_limit == 1:
				self.vel = 3

		if self.touch_pipe == 0:
			self.vel = 3

	def move(self):
		self.tick_count += 1
		d = self.vel * self.tick_count + 1.5*self.tick_count**2 

		if d >= 16: #terminal velocity
			d = 16

		self.y = self.y + d

	def draw(self, win):
		new_rect = self.img.get_rect(center= self.img.get_rect(topleft = (self.x, self.y)).center)
		win.blit(self.img, new_rect.topleft)

	def get_mask(self): #collision
		return pygame.mask.from_surface(self.img)

	def get_height(self, pipe_height):
		self.dist = self.y - pipe_height 

class Pipe:
	VEL = 5

	def __init__(self, x):
		self.height = 500
		self.gap = random.randrange(100, 200)
		self.x = x + self.gap
		self.x2 = self.x+PIPE_IMG.get_width()
		self.passed = False

	def collide(self, ball):
		ball_mask = ball.get_mask()
		pipe_mask = pygame.mask.from_surface(PIPE_IMG)

		offset = (self.x - ball.x, self.height - round(ball.y))

		c_point = ball_mask.overlap(pipe_mask, offset)

		if c_point:
			return True

		return False

	def move(self):
		self.x -= self.VEL

	def draw(self, win):
		win.blit(PIPE_IMG, (self.x, self.height))

	def width(self):
		self.x2 = self.x+PIPE_IMG.get_width()
		return self.x2

def draw_window(win, balls, pipes, score, gen):
	win.blit(BG_IMG, (0,0))
	for ball in balls:
		ball.draw(win)

	text = STAT_FONT.render("Distance travelled: "+ (str(score)), 1, (255,255,255)) #.render(value, Anti-Alias, Colour)
	win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

	text = STAT_FONT.render("Generation: "+ str(gen), 1, (255,255,255)) #.render(value, Anti-Alias, Colour)
	win.blit(text, (10, 10))

	for pipe in pipes:
		pipe.draw(win)
	pygame.display.update()

def main(genome, config):

	global GEN
	GEN += 1
	nets = []
	ge = []
	balls = []

	for _, g in genome:
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		balls.append(Ball(350, 230))
		g.fitness = 0
		ge.append(g)

	pipe_height = 500
	pipes = [Pipe(400), Pipe(800)]
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	clock = pygame.time.Clock()
	run=True
	score=0

	while run:
		clock.tick(30)
		score+=0.1
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()

		pipe_ind = 0
		
		if len(balls) > 0:
			if len(pipes) > 1 and balls[0].x > pipes[0].x + PIPE_IMG.get_width():
				pipe_ind = 1

		else:
			run=False
			break

		
		rem = []

		for pipe in pipes:
			pipe.move()

			if pipe.x + PIPE_IMG.get_width() < 0:
				translate_pipe = pipes[1].x + PIPE_IMG.get_width() + pipe.gap
				pipes.append(Pipe(translate_pipe))
				pipes.pop(0)

			for x, ball in enumerate(balls):	
				if pipe_ind == 1:
					ge[x].fitness += 5

				if pipe.collide(ball): 
					ball.touch_pipe = 1
					ball.test = 0
					ge[x].fitness += 1

					if ball.y >= pipe.height - 50:
						ball.y = pipe.height - 50


				ge[x].fitness += 1 #runs 30 times per second therefor lower fitness increase.
				
				ball.move()
			
				output = nets[x].activate((ball.y, abs(ball.y - pipes[0].height), abs(ball.y - pipes[pipe_ind].x), abs(ball.y - pipes[pipe_ind].width())))
				
				if ball.touch_pipe == 1:
					if output[0] > -0.7:
						ball.jump()

					else:
						ball.touch_pipe = 0

				if ball.y > 600:
					ge[x].fitness -= 100
					balls.pop(x)
					nets.pop(x)
					ge.pop(x)

		keys = pygame.key.get_pressed()
		
		draw_window(win, balls, pipes, math.trunc(score), GEN)


def run(config_path):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

	p = neat.Population(config)

	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)

	winner = p.run(main,50)
	neat.visualize

if __name__ == "__main__":
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, "config-feedforward.txt")
	run(config_path)
