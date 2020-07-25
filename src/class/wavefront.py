import time
import sys
import pygame
from math import sin, radians,degrees, copysign,cos,tan,fabs
import numpy

class Wavefront ():
    def __init__(self):
        pass


    def wave(self,goal,dist,mapOfWorld,width,height):

        map_name = "borda_black.jpg"
        background = pygame.image.load('../lib/map/'+ map_name +".jpg")
        mapOfWorld = pygame.surfarray.array3d(background)
        
        heap = []
        newheap = []
        print(goal)
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
                                #mapOfWorld[move[0]][move[1]] = (fabs(sin(radians(currentwave))*50),fabs(sin(radians(currentwave))*100),fabs(sin(radians(currentwave))*200))
                                newheap.append(move)
            '''                
            if currentwave%5 == 0:
                image = pygame.surfarray.make_surface(mapOfWorld)                
                image = pygame.transform.scale(image,(width, height))
                screen.blit(image, (0, 0))
                pygame.display.flip()
            '''    
            if(newheap == []):
                print ("Wavefront concluido")
                return matriz, #mapOfWorld
            heap = newheap
            newheap = []