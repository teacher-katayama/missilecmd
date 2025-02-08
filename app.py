"""Missile Command（ミサイルコマンド）
8割がたGPTx「Python」に書いてもらって、残り2割を自分で書いたものです。
"""

import random

import pyxel

SCREEN_WIDTH = 160  # 画面幅
SCREEN_HEIGHT = 120  # 画面高さ
EXPLOSION_SIZE = 9  # 爆発の大きさ


class MissileCommand:
    def __init__(self):
        """初期設定"""
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Missile Command")
        self.bases = [
            (20, SCREEN_HEIGHT - 10),
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 10),
            (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 10),
        ]  # 砲台の位置 (左, 中央, 右)
        self.aim = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]  # 照準の位置 (画面中央)
        self.reset()  # リセット処理
        pyxel.run(self.update, self.draw)

    def reset(self) -> None:
        """リセット処理"""
        self.missiles = []  # 敵ミサイル[始点x, 始点y, 終点x, 進行度]
        self.explosions = []  # 爆発エフェクト[座標x, 座標y, 大きさ]
        self.base_active = [True, True, True]  # 砲台の生存状態
        self.shots = []  # 発射された迎撃ミサイル[始点x, 始点y, 終点x, 終点y, 進行度]
        self.score = 0  # スコア
        self.game_over = False  # ゲームオーバー判定
        self.opening = True  # オープニング表示

    def update(self) -> None:
        """フレーム更新時に呼び出されるコールバック処理
        - 照準
        - 敵ミサイル
        - 迎撃ミサイル
        - 爆発の処理
        Memo
            PyxelのFPSのデフォルトは30
        """
        # ゲームオーバー
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.reset() # リセット処理
            return

        # オープニング
        if self.opening:
            self.update_aim()  # 照準の処理
            self.update_shots()  # 迎撃ミサイルの処理
            self.update_explosions()  # 爆発の処理
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.opening = False
            return

        self.update_aim()  # 照準の処理
        self.update_missiles()  # 敵ミサイルの処理
        self.update_shots()  # 迎撃ミサイルの処理
        self.update_explosions()  # 爆発の処理

    def update_aim(self) -> None:
        """照準に関する処理
        - マウスの位置に照準を合わせる
        """
        self.aim = [pyxel.mouse_x, pyxel.mouse_y]

    def update_shots(self) -> None:
        """迎撃ミサイルに関する処理
        - 迎撃ミサイルの発射を行う
        - 迎撃ミサイルの移動を行う
        """
        # 迎撃ミサイルの発射（z, x, c）
        if pyxel.btnp(pyxel.KEY_Z) and self.base_active[0]:
            self.shots.append(
                [self.bases[0][0], self.bases[0][1], self.aim[0], self.aim[1], 0]
            )
        if pyxel.btnp(pyxel.KEY_X) and self.base_active[1]:
            self.shots.append(
                [self.bases[1][0], self.bases[1][1], self.aim[0], self.aim[1], 0]
            )
        if pyxel.btnp(pyxel.KEY_C) and self.base_active[2]:
            self.shots.append(
                [self.bases[2][0], self.bases[2][1], self.aim[0], self.aim[1], 0]
            )

        # 迎撃ミサイルの移動
        for shot in self.shots[:]:
            shot[4] += 1  # 進行度を増加
            progress = shot[4] / 30  # 進行割合
            if progress > 1:
                progress = 1
            shot_x = shot[0] + (shot[2] - shot[0]) * progress
            shot_y = shot[1] + (shot[3] - shot[1]) * progress
            shot.append((shot_x, shot_y))
            if progress == 1:
                self.explosions.append([shot[2], shot[3], EXPLOSION_SIZE])
                self.shots.remove(shot)

    def update_explosions(self) -> None:
        """爆発に関する処理
        - 爆発の処理
        - 衝突判定
        """
        # 爆発の処理
        for explosion in self.explosions[:]:
            explosion[2] -= 1
            if explosion[2] <= 0:
                self.explosions.remove(explosion)

        # 衝突判定
        for missile in self.missiles[:]:
            for explosion in self.explosions:
                if (
                    abs(missile[2] - explosion[0]) < 8
                    and abs(missile[1] - explosion[1]) < 8
                ):
                    self.missiles.remove(missile)
                    self.score += 10
                    break

    def update_missiles(self) -> None:
        """敵ミサイルに関する処理
        - 敵ミサイルの追加
        - 敵ミサイルの移動
        """
        # 敵ミサイルの追加
        if random.random() < 0.02:
            start_x = random.randint(0, SCREEN_WIDTH)
            target_x = random.choice(
                [self.bases[0][0], self.bases[1][0], self.bases[2][0]]
            )
            self.missiles.append([start_x, 0, start_x, target_x, SCREEN_HEIGHT - 10])

        # 敵ミサイルの移動
        for missile in self.missiles[:]:
            missile[2] += (missile[3] - missile[2]) / 50  # X方向の移動
            missile[1] += 1  # Y方向の移動
            if missile[1] >= missile[4]:
                hit = False
                for i, (bx, by) in enumerate(self.bases):
                    if self.base_active[i] and abs(missile[2] - bx) < 8:
                        self.base_active[i] = False  # 砲台破壊
                        hit = True
                        break
                if hit:
                    self.missiles.remove(missile)
                else:
                    self.missiles.remove(missile)  # 砲台に当たらなかったミサイルを削除
                    self.game_over = all(not active for active in self.base_active)

    def draw(self) -> None:
        """画面描画のコールバック処理
        以下の順に重ねて描画する（＝実装はこの逆順で行っている）
        - オープニング/ゲームオーバー
        - スコア
        - 爆発
        - 照準
        - 敵ミサイル
        - 砲台
        - 迎撃ミサイル
        """
        pyxel.cls(pyxel.COLOR_BLACK)

        self.draw_shot()  # 迎撃ミサイル描画
        self.draw_base()  # 砲台描画
        self.draw_missile()  # 敵ミサイル描画
        self.draw_aim()  # 照準の描画
        self.draw_explosion()  # 爆発描画
        self.draw_score()  # スコア表示

        # ゲームオーバー表示
        if self.game_over:
            pyxel.text(
                SCREEN_WIDTH // 2 - 20,
                SCREEN_HEIGHT // 2 - 5,
                "GAME OVER",
                pyxel.COLOR_RED,
            )
            pyxel.text(
                SCREEN_WIDTH // 2 - 30,
                SCREEN_HEIGHT // 2 + 5,
                "Press Space Bar",
                pyxel.COLOR_WHITE,
            )
        # オープニング表示
        elif self.opening:
            pyxel.text(
                SCREEN_WIDTH // 2 - 30,
                SCREEN_HEIGHT // 2 - 5,
                "Missile Command",
                pyxel.COLOR_WHITE,
            )
            pyxel.text(
                SCREEN_WIDTH // 2 - 30,
                SCREEN_HEIGHT // 2 + 5,
                "Press Space Bar",
                pyxel.COLOR_WHITE,
            )

    def draw_aim(self) -> None:
        """照準の描画"""
        pyxel.line(
            self.aim[0] - 2, self.aim[1], self.aim[0] + 2, self.aim[1], pyxel.COLOR_LIME
        )
        pyxel.line(
            self.aim[0], self.aim[1] - 2, self.aim[0], self.aim[1] + 2, pyxel.COLOR_LIME
        )

    def draw_base(self) -> None:
        """砲台の描画"""
        for i, (bx, by) in enumerate(self.bases):
            if self.base_active[i]:
                pyxel.rect(bx - 5, by, 10, 5, pyxel.COLOR_ORANGE)

    def draw_shot(self) -> None:
        """迎撃ミサイルの描画"""
        for shot in self.shots:
            start_x, start_y = shot[0], shot[1]
            for i in range(5, len(shot), 1):
                pyxel.line(start_x, start_y, shot[i][0], shot[i][1], pyxel.COLOR_YELLOW)
                start_x, start_y = shot[i][0], shot[i][1]

    def draw_explosion(self) -> None:
        """爆発の描画"""
        for explosion in self.explosions:
            pyxel.circ(explosion[0], explosion[1], explosion[2], pyxel.COLOR_WHITE)

    def draw_missile(self) -> None:
        """敵ミサイルの描画"""
        for missile in self.missiles:
            pyxel.line(missile[0], 0, missile[2], missile[1], pyxel.COLOR_RED)

    def draw_score(self) -> None:
        """スコアの描画"""
        pyxel.text(5, 5, f"Score: {self.score}", pyxel.COLOR_WHITE)


MissileCommand()
