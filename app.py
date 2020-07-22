import os
import pygame
from pygame.math import Vector2
import time
import sys
from math import sin, radians,degrees, copysign,cos,tan,fabs
import numpy

class Sensor(pygame.sprite.Sprite):
    def __init__(self,init_position,max_length,angle,car_angle=0):
        pygame.sprite.Sprite.__init__(self)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "src/lib/sensor/sensor.png")        
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image,(10,10))
        self.rect = self.image.get_rect()
        self.rect.center = (self.rect.width / 2 , self.rect.height / 2)
        self.mask = pygame.mask.from_surface(self.image)
        self.color = (255,255,0)
        self.car_angle = car_angle
        self.angle = angle
        self.max_length = max_length
        self.length = 0
        self.init_position = init_position
        self.x = (cos(radians(self.angle+self.car_angle))*self.max_length)
        self.y = -(sin(radians(self.angle+self.car_angle))*self.max_length)
        self.rect.x = self.init_position[0] + self.x
        self.rect.y = self.init_position[1] + self.y

    def update(self,init_position):
        self.x = (cos(radians(self.angle+self.car_angle))*self.max_length)
        self.y = -(sin(radians(self.angle+self.car_angle))*self.max_length)
        self.init_position = init_position
        #self.rect.x = self.x + car_position[0]
        #self.rect.y = self.y + car_position[1]

        pass

class Car(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0.0, length=4, max_steering=30, max_acceleration=5.0):
        pygame.sprite.Sprite.__init__(self)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "src/lib/car/car1.png")        
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rotated = pygame.transform.rotate(self.image, angle)
        self.rect = self.rotated.get_rect()            
        self.rect.center = (self.rect.width / 2 , self.rect.height / 2)
        self.mask = pygame.mask.from_surface(self.rotated)
        self.position = Vector2(x, y)
        self.velocity = Vector2(0.0, 0.0)
        self.x = x
        self.y = y
        self.angle = angle
        self.length = length
        self.max_acceleration = max_acceleration
        self.max_steering = max_steering
        self.max_velocity = 20
        self.brake_deceleration = 40
        self.free_deceleration = 20
        self.angular_velocity = 0
        self.sensor_group = pygame.sprite.Group()
        self.sensor_group.add(
                                Sensor(self.rect.center,200,-45),
                                Sensor(self.rect.center,200,0),
                                Sensor(self.rect.center,200,45),
                                #Sensor(self.rect.center,200,135),
                                #Sensor(self.rect.center,200,-135)
                            )


        self.acceleration = 0.0
        self.steering = 0.0

    def update(self, dt,mapp):
        self.velocity += (self.acceleration * dt, 0)
        self.velocity.x = max(-self.max_velocity, min(self.velocity.x, self.max_velocity))

        if self.steering:
            turning_radius = self.length / sin(radians(self.steering))
            self.angular_velocity = self.velocity.x / turning_radius
        else:
            self.angular_velocity = 0

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += degrees(self.angular_velocity) * dt
        for sensor in self.sensor_group:
            sensor.car_angle = self.angle
            sensor.update(self.rect.center)


        self.rect.center = (self.rect.width / 2 , self.rect.height / 2)
        self.rotated = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.rotated.get_rect()
        self.rect[0],self.rect[1] = (self.position[0]*10 - self.rect.center[0],self.position[1]*10 - self.rect.center[1])
        self.mask = pygame.mask.from_surface(self.rotated)
        
    def get_car_data(self):
        sensor_data = list()
        for sensor in self.sensor_group:
            sensor_data.append(sensor.length)

        data = {

            'velocity': self.velocity.x,
            'acceleration': self.acceleration,
            'angular_velocity': self.angular_velocity,
            'distance': sensor_data,
            'steering': self.steering,
        }
        return data 
            
    def verify_sensors_limit(self,sensor,screen,background):
        normalized_vector = Vector2(sensor.x,sensor.y).normalize()
        vector = normalized_vector

        while vector.length() < sensor.max_length:
            #print(screen.get_at((int(sensor.init_position[0]]+vector.x),int(sensor.init_position[1]+vector.y))))

            
            if (int(sensor.init_position[0]+vector.x) >= 1279 or  int(sensor.init_position[0]+vector.x) <= 0) or int(sensor.init_position[1]+vector.y) >= 720 or int(sensor.init_position[1]+vector.y) <= 0:
                #return (int(sensor.init_position[0]]+vector.x),int(sensor.init_position[1]+vector.y))
                return (50,50)
            if background.get_at((int(sensor.init_position[0]+vector.x),int(sensor.init_position[1]+vector.y))) == (0,0,0,255):
                #pygame.draw.line(screen,sensor.color_limit,self.position * 10,(int(sensor.init_position[0]]+vector.x),int(sensor.init_position[1]+vector.y)),3)     
                sensor.length = vector.length()       
                return (int(sensor.init_position[0]+vector.x),int(sensor.init_position[1]+vector.y))
            vector+=normalized_vector*0.01
                        
            
            #pygame.draw.line(screen,sensor.color_limit,self.position * 10,(int(sensor.init_position[0]]+vector.x),int(sensor.init_position[1]+vector.y)),3)
        sensor.length = vector.length()
        return (int(sensor.init_position[0]+sensor.x),int(sensor.init_position[1]+sensor.y))

    def front(self,dt):
        if self.velocity.x < 0:
            self.acceleration = self.brake_deceleration
        elif(self.velocity.x > 0 and self.brake_deceleration > 0 ):
            self.acceleration += self.brake_deceleration + (1 * dt)
        else:
            self.acceleration += 1 * dt
    def back(self,dt):
        if self.velocity.x > 0:
            self.acceleration = -self.brake_deceleration
        elif(self.velocity.x < 0 and self.brake_deceleration > 0 ):
            self.acceleration -= self.brake_deceleration + (1 * dt)
        else:
            self.acceleration -= 1 * dt
    def right(self,dt):
        self.steering -= 30 * dt
        pass
    def left(self,dt):
        self.steering += 30 * dt
        pass
    def breaker(self,dt):
        if abs(self.velocity.x) > dt * self.brake_deceleration:
            self.acceleration = -copysign(self.brake_deceleration, self.velocity.x)
        else:
            self.acceleration = -self.velocity.x / dt
    
    def conserve_energy(self,dt):
        
        if abs(self.velocity.x) > dt * self.free_deceleration:
            self.acceleration = -copysign(self.free_deceleration, self.velocity.x)
        else:
            if dt != 0:
                self.acceleration = -self.velocity.x / dt

class Map(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "src/lib/map/borda.png")        
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)


    def update(self):
        pass

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Car tutorial")
        self.width = 1280
        self.height = 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.background = pygame.image.load('src/lib/map/trajeto_1.jpg')
        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False
        self.font = pygame.font.SysFont(None, 24)
        
        self.array_map = pygame.surfarray.array3d(self.background)

    def run(self):
        car_group = pygame.sprite.Group()
        car = Car(70, 10)
        car_group.add(car)
        map_group = pygame.sprite.Group()
        mapp = Map()
        map_group.add(mapp)
        ppu = 10

        while not self.exit:
            dt = self.clock.get_time() / 1000

            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            # User input
            pressed = pygame.key.get_pressed()

            if pressed[pygame.K_UP]:
                car.front(dt)
            elif pressed[pygame.K_DOWN]:
                car.back(dt)
            elif pressed[pygame.K_SPACE]:
                car.breaker(dt)
            else:
                car.conserve_energy(dt)
                    
            car.acceleration = max(-car.max_acceleration, min(car.acceleration, car.max_acceleration))

            if pressed[pygame.K_RIGHT]:
                car.right(dt)
            elif pressed[pygame.K_LEFT]:
                car.left(dt)
            elif car.steering > 1:
                car.steering -= 60 * dt
            elif car.steering < -1:
                car.steering += 60 * dt
            elif car.steering < 1 or car.steering > -1:
                car.steering = 0
            
            car.steering = max(-car.max_steering, min(car.steering, car.max_steering))
            i=0

            if pygame.sprite.groupcollide(map_group,car_group,False,False,pygame.sprite.collide_mask):
                # Logica de colisão
                break
            else:
                pass

            # Logic
            car.update(dt,mapp)

            # Drawing
            self.screen.fill((255, 255, 255))
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(car.rotated,(car.rect[0],car.rect[1]))
            #car.sensor_group.draw(self.screen)
            
            for sensor in car.sensor_group:
                pygame.draw.line(self.screen,sensor.color,sensor.init_position,car.verify_sensors_limit(sensor,self.screen,self.background),3)
                pass

            car_data = car.get_car_data()
            i = 200
            j = 1

            pygame.draw.rect(self.screen, (10,10,10), (280,190,350,175))
            for sensor_data in car_data['distance']:
                img = self.font.render(str("distance: "+str(j)+": "+str(sensor_data)) , True, (189, 117, 9))
                self.screen.blit(img, (300, i))
                i += 20
                j += 1
            i += 20
            img1 = self.font.render("Velocity: "+str(car_data['velocity']) , True, (189, 117, 9))
            self.screen.blit(img1, (300, i))
            i += 20
            img2 = self.font.render("Angular Velocity: "+str(car_data['angular_velocity']) , True, (189, 117, 9))
            self.screen.blit(img2, (300, i))
            i += 20
            img3 = self.font.render("Acceleration: "+str(car_data['acceleration']) , True, (189, 117, 9))
            self.screen.blit(img3, (300, i))
            i += 20
            img4 = self.font.render("Steering: "+str(car_data['steering']) , True, (189, 117, 9))
            self.screen.blit(img4, (300, i))
            
            img5 = self.font.render(str(int(self.clock.get_fps())) , True, (189, 117, 9))
            self.screen.blit(img5, (0, 0))


            pygame.display.flip()
            self.clock.tick(self.ticks)
       


if __name__ == '__main__':    
    game = Game()
    while not game.exit:
        game.run()

    pygame.quit()