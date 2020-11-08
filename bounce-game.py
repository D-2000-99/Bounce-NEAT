import pygame
import neat
import time
import os
import random
import math
pygame.font.init()

WIN_WIDTH = 800
WIN_HEIGHT = 600
BALL_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "ball.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "BG.png")))
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe1.png")))
STAT_FONT = pygame.font.SysFont("comicsans", 50)

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
		self.touch_pipe = 0
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
		self.gap = random.randrange(100, 300)
		self.x = x + self.gap
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


def draw_window(win, ball, pipes, score):
	win.blit(BG_IMG, (0,0))
	ball.draw(win)
	text = STAT_FONT.render("Distance travelled: "+ (str(score)), 1, (0,0,0)) #.render(value, Anti-Alias, Colour)
	win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

	for pipe in pipes:
		pipe.draw(win)
	pygame.display.update()

def main():

	pipe_height = 500
	ball = Ball(350, 230)
	pipes = [Pipe(400), Pipe(1000)]
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	clock = pygame.time.Clock()
	run=True
	score=0
	ball.touch_pipe = 1


	while run:
		clock.tick(30)    
		score+=0.1 
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()

		ball.move();
		for pipe in pipes:
			pipe.move()

			if pipe.x + PIPE_IMG.get_width() < 0:
				translate_pipe = pipes[1].x + PIPE_IMG.get_width() + pipe.gap
				print(translate_pipe)
				pipes.append(Pipe(translate_pipe))
				pipes.pop(0)

			if pipe.collide(ball): 
				ball.touch_pipe = 1
				ball.test = 0

				if ball.y >= pipe.height - 50:
					ball.y = pipe.height - 50

		keys = pygame.key.get_pressed()
		
		if ball.touch_pipe == 1:

			if event.type == pygame.KEYDOWN:
				if keys[pygame.K_SPACE]:
					ball.jump()

			if event.type == pygame.KEYUP:
				ball.touch_pipe = 0

			
		draw_window(win, ball, pipes, math.trunc(score))

main()