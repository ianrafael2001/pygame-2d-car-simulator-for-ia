import time
import sys
import pygame
from math import sin, radians,degrees, copysign,cos,tan,fabs
import numpy

def wave(goal,dist,mapOfWorld,screen,width,height):
    heap = []
    newheap = []
    x, y = goal
    lastwave = 3
    width = width
    height = height


    matriz = []
    for _ in range(width):
        line = []
        for __ in range(height):
            line.append(0)
        matriz.append(line)

    # Start out by marking nodes around G with a 3
    moves = [[x + 1, y], [x - 1, y], [x, y - 1], [x, y + 1]]
    pixels=[]
    #pixels = [(80,11),(80,12),(80,13),(80,14)]
    for i in range(1,dist+1):
        pixels.append((x,y+i))

    for pixel in pixels:
        x,y = pixel
        moves.append([x + 1, y])
        moves.append([x - 1, y])
        moves.append([x, y - 1])
        moves.append([x, y + 1])
    for move in moves:
        if not numpy.array_equal(mapOfWorld[move[0]][move[1]],(0,0,0)):
            matriz[move[0]][move[1]] = 3
            #mapOfWorld[move[0]][move[1]] = (0, (255-3)%255, 3%255)
            heap.append(move)
        

    
    for currentwave in range(4, int((width*height)/2)):
        lastwave = lastwave + 1
        while(heap != []):
            position = heap.pop()
            (x, y) = position
            moves = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            #x, y = position

            for move in moves:
                if (move[0] < width and move[0] >= 0)  and (move[1] < height and move[1] >= 0):
                    if not numpy.array_equal(mapOfWorld[move[0]][move[1]],(0,0,0)) and  numpy.array_equal(matriz[move[0]][move[1]],0):
                        if not (numpy.array_equal(mapOfWorld[move[0]][move[1]],(0,0,0))) and numpy.array_equal(matriz[position[0]][position[1]],(currentwave - 1)):
                            matriz[move[0]][move[1]] = (currentwave)
                            mapOfWorld[move[0]][move[1]] = (fabs(sin(radians(currentwave))*50),fabs(sin(radians(currentwave))*100),fabs(sin(radians(currentwave))*200))
                            newheap.append(move)
                           
        if currentwave%1 == 0:
            image = pygame.surfarray.make_surface(mapOfWorld)                
            image = pygame.transform.scale(image,(width*7, height*7))
            screen.blit(image, (0, 0))
            pygame.display.flip()
            
        if(newheap == []):
            print ("Goal is unreachable")
            return matriz, mapOfWorld
        heap = newheap
        newheap = []

pygame.display.set_caption("Car tutorial")
width = 200
height = 120
screen = pygame.display.set_mode((width*7, height*7))
background = pygame.image.load('wavefront_1.jpg')
clock = pygame.time.Clock()
ticks = 30
exit = False
array_map = pygame.surfarray.array3d(background)
print(len(array_map),len(array_map[1]))
pygame.init()
run_performace,world = wave((102,11),10,array_map,screen,width,height)
print("desenhando onda...")

image = pygame.surfarray.make_surface(world)
image = pygame.transform.scale(image,(width*7, height*7))
while not exit:
    dt = clock.get_time() / 1000

    # Event queue
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = True

    # Drawing
    screen.blit(image, (0, 0))
    
    pygame.display.flip()
    clock.tick(ticks)