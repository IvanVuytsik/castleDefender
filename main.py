import pygame
import math
from enemy import Enemy
import os
import random
import button

pygame.init()

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 600


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Castle Defender')

clock = pygame.time.Clock()
FPS = 60
level = 1
high_score = 0
level_difficulty = 0
target_difficulty = 1000
difficulty_multiplier = 1.25
game_over = False
next_level = False
# enemy generator
enemy_timer = 1000
last_enemy = pygame.time.get_ticks()
enemies_alive = 0

tower_cost = 5000
tower_positions = [
    [SCREEN_WIDTH - 250, SCREEN_HEIGHT - 500],
    [SCREEN_WIDTH - 200, SCREEN_HEIGHT - 550],
    [SCREEN_WIDTH - 150, SCREEN_HEIGHT - 400],
    [SCREEN_WIDTH - 100, SCREEN_HEIGHT - 300],
]

if os.path.exists('score.txt'):
    with open('score.txt', 'r') as f:
        high_score = int(f.read())



font_s = pygame.font.SysFont('Futura', 30)
font_l = pygame.font.SysFont('Futura', 60)



#------------------------imgs----------------------
bg_img = pygame.image.load('img/bg.png').convert_alpha()
bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH,SCREEN_HEIGHT))

bullet_img = pygame.image.load('img/bullet.png').convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (int(bullet_img.get_width()*0.075),int(bullet_img.get_height()*0.075)))

repair_img = pygame.image.load('img/repair.png').convert_alpha()

armour_img = pygame.image.load('img/armour.png').convert_alpha()

#--------------foes(attack/death/walk)------------
enemy_animations = []
enemy_types = ['gladiator_a', 'gladiator_b']
enemy_health = [100, 200]

animation_types = ['walk', 'attack', 'dead']
for enemy in enemy_types:
    animation_list = []
    for animation in animation_types:
        temp_list = []
        path, dirs, frames = next(os.walk(f'img/enemies/{enemy}/{animation}'))
        frames_count = len(frames)
        for i in range(frames_count):
            img = pygame.image.load(f'img/enemies/{enemy}/{animation}/{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width()*1),int(img.get_height()*1)))
            temp_list.append(img)
        animation_list.append(temp_list)
    enemy_animations.append(animation_list)



def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x,y))

def show_info():
    draw_text('Money: ' + str(castle.money), font_s, (0,200,0), 10,10)
    draw_text('Score: ' + str(castle.score), font_s, (0,200,0), 200,10)
    draw_text('High Score: ' + str(high_score), font_s, (0,200,0), 200,50)
    draw_text('Level: ' + str(level), font_s, (0, 200, 0), 400,10)
    draw_text('Health: ' + str(castle.health) + " / " + str(castle.max_health), font_s, (0,200,0), castle.rect.bottomleft,castle.rect.midbottom)
    draw_text('1000', font_s, (0,200,0), repair_button.rect.midright,repair_button.rect.midright)
    draw_text('1000', font_s, (0,200,0), armour_button.rect.midright,armour_button.rect.midright)
    draw_text('5000', font_s, (0,200,0), tower_button.rect.midright,tower_button.rect.midright)


#----------------classes----------------------
path, dirs, img = next(os.walk("img/castle"))
img_count = len(img)
castle_img = []
for x in range(img_count):
    img = pygame.image.load(f'img/castle/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (int(img.get_width()*0.2), int(img.get_height()*0.2)))
    castle_img.append(img)
class Castle():
    def __init__(self, x, y):
        self.img = castle_img[0]
        self.health = 1000
        self.max_health = self.health
        self.fired = False
        self.money = 5000
        self.score = 0
        self.rect = self.img.get_rect()
        self.rect.x = x
        self.rect.y = y

    def shoot (self):
        pos = pygame.mouse.get_pos()
        x_dist = pos[0] - self.rect.midleft[0]
        y_dist = -(pos[1] - self.rect.midleft[1])
        self.angle = math.degrees(math.atan2(y_dist, x_dist))

        if pygame.mouse.get_pressed()[0] and self.fired == False and pos[1] > 100:
            print(pos[1])
            self.fired = True
            bullet = Bullet(bullet_img, self.rect.midleft[0], self.rect.midleft[1], self.angle)
            bullet_group.add(bullet)
        if pygame.mouse.get_pressed()[0] == False:
            self.fired = False

        #pygame.draw.line(screen, (0,0,0), (self.rect.midleft[0], self.rect.midleft[1]), (pos))

    def draw(self):
        if self.health <= 250:
            self.img = castle_img[2]
        elif self.health <= 500:
            self.img = castle_img[1]
        else:
            self.img = castle_img[0]
        screen.blit(self.img, self.rect)


    def repair(self):
        if self.money >= 1000 and self.health < self.max_health:
           self.health += 500
           self.money -= 1000
           if self.health > self.max_health:
               self.health = self.max_health

    def armour(self):
        if self.money >= 1000:
            self.max_health += 250
            self.money -= 1000



#-----------------towers----------------------
path, dirs, img = next(os.walk("img/tower"))
img_count = len(img)
tower_img = []
for x in range(img_count):
    img = pygame.image.load(f'img/tower/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (int(img.get_width()*0.2), int(img.get_height()*0.2)))
    tower_img.append(img)

class Tower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = tower_img[0]
        self.target_acquired = False
        self.angle = 0
        self.last_shot = pygame.time.get_ticks()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, enemy_group):
        self.target_acquired = False
        for e in enemy_group:
            if e.alive == True:
               target_x, target_y = e.rect.midbottom
               self.target_acquired = True
               break
        if self.target_acquired:
            #pygame.draw.line(screen, (0,0,0), (self.rect.midleft[0], self.rect.midleft[1]), (target_x,target_y))
            x_dist = target_x - self.rect.midleft[0]
            y_dist = -(target_y - self.rect.midleft[1])
            self.angle = math.degrees(math.atan2(y_dist, x_dist))

            shot_cooldown = 1000
            if pygame.time.get_ticks() - self.last_shot > shot_cooldown:
                self.last_shot = pygame.time.get_ticks()
                bullet = Bullet(bullet_img, self.rect.midleft[0], self.rect.midleft[1], self.angle)
                bullet_group.add(bullet)


        if castle.health <= 250:
            self.image = tower_img[2]
        elif castle.health <= 500:
            self.image = tower_img[1]
        else:
            self.image = tower_img[0]



class Bullet(pygame.sprite.Sprite):
    def __init__(self, image, x, y, angle):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.angle = math.radians(angle)
        self.speed = 10
        # calc v/h speed
        self.dx = math.cos(self.angle) * self.speed
        self.dy = -(math.sin(self.angle) * self.speed)

    def update(self):
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()
        #move bullet
        self.rect.x += self.dx
        self.rect.y += self.dy

class Crosshair():
    def __init__(self, scale):
        crosshair_img = pygame.image.load('img/crosshair.png').convert_alpha()
        self.image = pygame.transform.scale(crosshair_img,
                                            (int(crosshair_img.get_width()*scale),
                                             int(crosshair_img.get_height()*scale)))
        self.rect = self.image.get_rect()
        pygame.mouse.set_visible(False)

    def draw(self):
        mx, my = pygame.mouse.get_pos()
        self.rect.center = (mx, my)
        screen.blit(self.image, self.rect)



#classes
castle = Castle(SCREEN_WIDTH-200, SCREEN_HEIGHT-400)
crosshair = Crosshair(0.025)

repair_button = button.Button(SCREEN_WIDTH-200,10,repair_img,0.5)
tower_button = button.Button(SCREEN_WIDTH-300,10,tower_img[0],0.4)
armour_button = button.Button(SCREEN_WIDTH-100,10,armour_img,1)

tower_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()





#loop
run = True
while run:
    clock.tick(FPS)
    if game_over == False:
        screen.blit(bg_img, (0,0))

        castle.draw()
        castle.shoot()
        tower_group.draw(screen)
        tower_group.update(enemy_group)

        crosshair.draw()

        bullet_group.draw(screen)
        bullet_group.update()
        #print(len(bullet_group))

        enemy_group.update(screen, castle, bullet_group)

        show_info()
        if repair_button.draw(screen):
            castle.repair()
        if tower_button.draw(screen):
            if castle.money >= tower_cost and len(tower_group) < len(tower_positions):

                tower = Tower(tower_positions[len(tower_group)][0],
                              tower_positions[len(tower_group)][1])
                tower_group.add(tower)

                castle.money -= tower_cost

        if armour_button.draw(screen):
            castle.armour()



        # enemy generator
        if level_difficulty < target_difficulty:
            if pygame.time.get_ticks() - last_enemy > enemy_timer:
                e = random.randint(0,len(enemy_types)-1)
                enemy = Enemy(enemy_health[e], enemy_animations[e], -100, SCREEN_HEIGHT-random.randint(100,400) , 1)
                enemy_group.add(enemy)
                last_enemy = pygame.time.get_ticks()
                # difficulty increase
                level_difficulty += enemy_health[e]


        if level_difficulty >= target_difficulty:
            enemies_alive = 0
            for e in enemy_group:
                if e.alive == True:
                    enemies_alive +=1
            if enemies_alive == 0 and next_level == False:
                next_level = True
                level_reset_time = pygame.time.get_ticks()

        if next_level == True:
            draw_text('LEVEL COMPLETE', font_l, (255,255,255), SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2)
            if castle.score > high_score:
                high_score = castle.score
                with open('score.txt', 'w') as f:
                    f.write(str(high_score))


            if pygame.time.get_ticks() - level_reset_time > 1500:
                next_level = False
                level += 1
                last_enemy = pygame.time.get_ticks()
                target_difficulty *= difficulty_multiplier
                level_difficulty = 0
                enemy_group.empty()

        if castle.health <= 0:
            game_over = True
    else:
        draw_text('GAME OVER', font_l, (255,255,255), 300,300)
        draw_text('PRESS "A" TO PLAY', font_l, (255,255,255), 300,350)
        pygame.mouse.set_visible(True)
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
           game_over = False
           level = 1
           target_difficulty = 1000
           level_difficulty = 0
           last_enemy = pygame.time.get_ticks()
           enemy_group.empty()
           tower_group.empty()
           castle.score = 0
           castle.health = 1000
           castle.max_health = castle.health
           castle.money = 5000
           pygame.mouse.set_visible(True)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False


    #----------------display update
    pygame.display.update()

pygame.quit()

