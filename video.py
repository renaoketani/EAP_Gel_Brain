import pandas as pd
import cv2
import numpy as np
import os
import glob
import time
from scipy import optimize as opt

def create_replay_video(combine_pong_1751):
    if not os.path.exists(combine_pong_1751):
        print(f"【エラー】ファイルが見つかりません: {combine_pong_1751}")
        return

    # 出力ファイル名を CSV名_accurate_sync.mp4 に設定
    output_name = f"{os.path.splitext(combine_pong_1751)[0]}_accurate_sync.mp4"

    print(f"【1/4】解析開始: {combine_pong_1751}")
    print(f" -> 完成予定ファイル: {output_name}")

    try:
        df = pd.read_csv(combine_pong_1751)
        df.columns = df.columns.str.strip()
        total_rows = len(df)
    except Exception as e:
        print(f"【エラー】読み込み失敗: {e}")
        return

    # ベースライン計算（最初の10行の平均を基準にする）
    c_blk, c_brn, c_red = df['cBlack'].values, df['cBrown'].values, df['cRed'].values
    orig_blk, orig_brn, orig_red = np.mean(c_blk[:10]), np.mean(c_brn[:10]), np.mean(c_red[:10])

    # 設定値 (100Hzデータを30fps動画にする)
    data_freq, fps = 100, 30
    draw_size, graph_size = 600, 600
    y_min, y_max = -15, 10
    display_sec, history_rows = 60, 6000

    b_x, b_y = df['BallX'].values, df['BallY'].values
    relly_col = next((c for c in df.columns if c.lower().replace(' ', '') in ['rellycount', 'rallycount']), None)
    r_counts = df[relly_col].values if relly_col else np.zeros(total_rows)

    ORIG_H, P_HEIGHT, lowRangeC = 1000, 333, 10.0
    X_SENSORS = np.array([166, 500, 833]) # 1/6, 3/6, 5/6
    DISP_X = np.linspace(0, ORIG_H, 50)

    def map_current_refined(val, orig):
        maxC, minC = orig, orig - lowRangeC
        temp = (val - minC) / (maxC - minC)
        return max(0.0, min(1.0, temp))

    def fit_func(x, a, b, c):
        return a * np.power(x, 2) + b * x + c

    # 動画書き出し準備
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_name, fourcc, fps, (draw_size + graph_size, draw_size))

    # グラフ背景
    bg_base = np.full((draw_size, graph_size, 3), (255, 255, 255), dtype=np.uint8)
    m_l, m_r, m_t, m_b = 65, 30, 70, 65
    g_w, g_h = graph_size - m_l - m_r, draw_size - m_t - m_b
    for v in range(int(y_min), int(y_max) + 1):
        py = draw_size - m_b - int((v - y_min) / (y_max - y_min) * g_h)
        cv2.line(bg_base, (m_l, py), (graph_size - m_r, py), (240, 240, 240), 1)
        cv2.putText(bg_base, str(v), (m_l - 35, py + 5), 1, 0.8, (0,0,0), 1)

    print(f"【2/4】動画作成中...")
    start_t = time.time()
    current_idx_float = 0.0

    while int(current_idx_float) < total_rows:
        idx = int(current_idx_float)
        try:
            # センサー値からパドル位置を計算
            y_fit = np.array([
                map_current_refined(c_blk[idx], orig_blk),
                map_current_refined(c_brn[idx], orig_brn),
                map_current_refined(c_red[idx], orig_red)
            ])
            popt, _ = opt.curve_fit(fit_func, X_SENSORS, y_fit, maxfev=500)
            dispY = fit_func(DISP_X, *popt)
            raw_pos = DISP_X[np.argmax(dispY)] - (P_HEIGHT / 2)
            paddle_y = int(max(0, min(ORIG_H - P_HEIGHT, raw_pos)))
        except:
            paddle_y = paddle_y if 'paddle_y' in locals() else 333

        # ゲーム画面描画
        game_f = np.full((ORIG_H, ORIG_H, 3), (255, 186, 111), dtype=np.uint8)
        cv2.line(game_f, (500, 0), (500, 1000), (0, 0, 0), 3)
        for h in [333, 666]: cv2.line(game_f, (0, h), (1000, h), (0, 0, 0), 3)
        cv2.rectangle(game_f, (10, paddle_y), (35, paddle_y + P_HEIGHT), (255, 255, 255), -1)
        cv2.rectangle(game_f, (int(b_x[idx]), int(b_y[idx])), (int(b_x[idx])+35, int(b_y[idx])+35), (255, 255, 255), -1)
        cv2.putText(game_f, str(int(r_counts[idx])), (470, 90), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 5)
        game_f = cv2.resize(game_f, (draw_size, draw_size))

        # グラフ画面描画
        graph_f = bg_base.copy()
        ts = idx / data_freq
        d_start = max(0, ts - display_sec)
        p_idx = np.arange(max(0, idx - history_rows), idx + 1, 4)
        if len(p_idx) > 1:
            x_pts = (m_l + (p_idx / data_freq - d_start) / display_sec * g_w).astype(np.int32)
            for d, col in [(c_blk, (0,0,0)), (c_brn, (42,42,165)), (c_red, (0,0,255))]:
                y_pts = (draw_size - m_b - ((d[p_idx] - y_min) / (y_max - y_min) * g_h)).astype(np.int32)
                cv2.polylines(graph_f, [np.column_stack([x_pts, y_pts])], False, col, 1, cv2.LINE_AA)

        # 枠線と時間を最後に描画
        cv2.rectangle(graph_f, (m_l, m_t), (draw_size - m_r, draw_size - m_b), (0, 0, 0), 2)
        cv2.putText(graph_f, f"Time: {ts:.1f}s", (m_l, m_t - 15), 1, 1.2, (0,0,0), 1)

        out.write(np.hstack((game_f, graph_f)))
        current_idx_float += (data_freq / fps)

        if idx % 1000 == 0:
            eta = ((time.time()-start_t)/(idx+1)*(total_rows-idx)) if idx > 0 else 0
            print(f"\r進捗: {(idx/total_rows)*100:5.1f}% | 残り推定: {int(eta)}秒 ", end="")

    out.release()
    print(f"\n【完了】動画を保存しました: {output_name}")

if __name__ == "__main__":
    # 指定されたファイル名を直接ターゲットにする
    target = "combine_pong_1751.csv"
    create_replay_video(target)