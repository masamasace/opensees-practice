# OpenseesPy関連のメモ

## 2024/07/04

- 目標：OpenseesPyで、単純せん断試験のシミュレーションを行う

- `op.wipe()`はなぜ必要？
    - `op.wipe()`は、OpenseesPyのメモリをクリアする関数
    - これを実行しないと、前回の解析結果が残ってしまう
- `op.model('basic','-ndm',2,'-ndf',3)`はどのような意味を持つ？
    - `op.model('basic')`は、モデルの初期化を行う関数
    - `-ndm`は、次元数を指定するオプション
    - `-ndf`は、自由度の数を指定するオプション
- `op.node(1,0,0)`について
    - `op.node(1,0,0)`は、節点を定義する関数
    - `1`は、節点のID。整数である必要がある。
    - `0,0`は、節点の座標。可変長引数であるため、次元数に応じて座標を指定する。
- `op.fix(1, 1, 1)`について
    - `op.fix(1, 1, 1)`は、節点の拘束条件を設定する関数
    - `1`は、節点のID
    - `1,1`は、拘束条件。`1`は拘束、`0`は拘束なしを意味する。
- `op.nDMaterial('PM4Sand', 1, D_r, G_o, h_po, Den, P_atm, h_o, e_max, e_min, n_b, n_d, A_do, z_max, c_z, c_e, phi_cv, nu, g_degr, c_dr, c_kaf, Q_bolt, R_bolt, m_par, F_sed, p_sed)`について
    - `op.nDMaterial()`は、構成則を設定する関数
    - `PM4Sand`以外にも多くの構成則が使用可能
        - [参考](https://openseespydoc.readthedocs.io/en/latest/src/ndMaterial.html)
    - `1`は、材料のID。整数でないといけない
    - `D_r`は、相対密度
    - `G_o`は、地盤のせん断剛性率
    - `h_po`は、Contraction rate parameter
    - `Den`は、材料の密度
    - (これ以降はoptionalな変数)
        - `P_atm`は、大気圧
        - (以下省略)
- `op.element('quad', 1, 1, 2, 3, 4, 1.0, 'PlaneStrain', 1, 0.0, rho, 0.0, -9.81)`について
        - 


- `op.timeSeries('Linear', 1)`について