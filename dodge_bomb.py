import os
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650 #サイズ
DELTA = {
    pg.K_UP: (0, -5), 
    pg.K_DOWN: (0, +5), 
    pg.K_LEFT:(-5, 0), 
    pg.K_RIGHT:(+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数で与えられたRectが画面の中か外かを判定する
    引数:こうかとんRect or 爆弾Rect
    戻り値:真理値タプル(横、縦)/画面内:True, 画面買い:False
    """
    yoko,tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko =False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate
    

def game_over(screen: pg.Surface) -> None:
    """
    ゲームオーバー時に、半透明の黒い画面上に「Game Over」と表示し、泣いているこうかとん画像を貼り付ける関数
    引数:screen Surface
    戻り値:なし
    """
    naki_img = pg.image.load("fig/8.png") #泣いてるこうかとん画像
    naki_img = pg.transform.rotozoom(naki_img, 0, 0.9)
    haikei = pg.Surface((WIDTH, HEIGHT)) #ゲームオーバーSurface
    pg.draw.rect(haikei, (0, 0, 0), pg.Rect(0, 0, 1100, 650)) #黒い画面
    haikei.set_alpha(128) #背景を半透明に
    fonto = pg.font.Font(None, 80) #font設定
    txt = fonto.render("Game Over", True, (255, 255, 255)) #文字Surface
    txt_rct = txt.get_rect() 
    txt_rct.center = WIDTH/2, HEIGHT/2 #文字の中心をサイズの真ん中に
    naki_rct = naki_img.get_rect()
    naki_rct.center = WIDTH/2 - 200, HEIGHT/2 #画面の中心をサイズの真ん中に
    screen.blit(haikei, [0, 0])
    screen.blit(txt, txt_rct)
    screen.blit(naki_img, naki_rct)
    naki_rct.center = WIDTH/2 + 200, HEIGHT/2 #画面の中心をサイズの真ん中に
    screen.blit(naki_img, naki_rct)
    pg.display.update()
    time.sleep(5)


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    サイズの異なる爆弾Surfaceを要素としたリストと加速度リストを返す
    引数:None
    戻り値:爆弾Surfaceのリストと加速度リストのタプル
    """
    bb_surface = []
    accs = [a for a in range(1, 11)] #加速度のリスト
    for r in range(1, 11): #拡大爆弾Surfaceのリスト
        bb_img = pg.Surface((20*r, 20*r)) #空のSurface
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0)) #四隅の黒を透過させる
        bb_surface.append(bb_img)
    return bb_surface, accs


def get_kk_img(sum_mv: tuple[int, int]) -> pg.Surface:
    """
    移動量の合計値タプルに対応する向きの画像Surfaceを返す
    """
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    #押下キーに対する移動量の合計値タプルをキー，rotozoomしたSurfaceを値とした辞書
    KEY = {
        (0, 0): pg.transform.rotozoom(kk_img, 0, 1.0),
        (0, -5): pg.transform.rotozoom(kk_img, 270, 1.0),
        (+5, -5): pg.transform.rotozoom(kk_img, 315, 1.0),
        (+5, 0): pg.transform.rotozoom(kk_img, 180, 1.0),
        (+5, +5): pg.transform.rotozoom(kk_img, 45, 1.0),
        (0, +5): pg.transform.rotozoom(kk_img, 90, 1.0),
        (-5, +5): pg.transform.rotozoom(kk_img, 45, 1.0),
        (-5, 0): pg.transform.rotozoom(kk_img, 0, 1.0),
        (-5, -5): pg.transform.rotozoom(kk_img, 315, 1.0),
    }
    kk_img = KEY[tuple(sum_mv)] #辞書から取ってくる
    #向きを変える
    if(tuple(sum_mv)==(0, +5)or(tuple(sum_mv)==(0, -5))or(tuple(sum_mv)==(+5, -5))or(tuple(sum_mv)==(+5, +5))):
        kk_img = pg.transform.flip(kk_img, True, False)
    elif(tuple(sum_mv)==(+5, 0)):
        kk_img = pg.transform.flip(kk_img, False, True)
    return kk_img
    

def main():
    pg.display.set_caption("逃げろ！こうかとん") #タイトル
    screen = pg.display.set_mode((WIDTH, HEIGHT)) #screen surface
    bg_img = pg.image.load("fig/pg_bg.jpg") #画像Surface 
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200 #初期座標
    bb_img = pg.Surface((20, 20)) #爆弾用の空のSurface
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10) #爆弾円を描く
    bb_img.set_colorkey((0, 0, 0)) #四隅の黒を透過させる
    bb_imgs, bb_accs = init_bb_imgs() #爆弾のサイズと加速度を新しく設定する
    bb_rct = bb_img.get_rect() #爆弾が存在する範囲を取得
    bb_rct.center = (random.randint(0, WIDTH), random.randint(0, HEIGHT)) #タプルでランダムな中心位置をcenterに渡している
    vx, vy = +5, +5 #爆弾速度ベクトル
    clock = pg.time.Clock()
    tmr = 0


    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        #別のRectオブジェクトと重なっているか判定する      
        if kk_rct.colliderect(bb_rct):
            game_over(screen) #ゲームオーバー関数
            print("ゲームオーバー")
            return #ゲームオーバー
        screen.blit(bg_img, [0, 0]) #screenにbg_imgのSurfaceを貼りつける
        key_lst = pg.key.get_pressed() #すべてのキーの押下状態を取得する
        sum_mv = [0, 0]
        #DELTAという辞書をfor文で回す((K_UP, (0, -5))
        for key, tpl in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]
        kk_img = get_kk_img((0, 0))
        kk_img = get_kk_img(tuple(sum_mv))
        print(sum_mv)
        print(get_kk_img(sum_mv))
        kk_rct.move_ip(sum_mv) #移動させる
        #こうかとんが画面外なら、元の場所に戻す
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct) #screenにkk_imgのSurfaceを貼りつける
        #爆弾拡大
        avx = vx*bb_accs[min(tmr//500, 9)] #新しい加速度
        bb_img = bb_imgs[min(tmr//500, 9)]
        bb_rct.move_ip(avx, vy) #爆弾の速度
        yoko, tate = check_bound(bb_rct)
        if not yoko: #横にはみ出てる
            vx *= -1
        if not tate: #縦にはみ出てる
            vy *= -1
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
