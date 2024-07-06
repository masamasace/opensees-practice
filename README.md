# OpenseesPy関連の学習記録

## 最初に読んでおくべき内容

### 公式関連の参考資料
- [https://opensees.berkeley.edu/](https://opensees.berkeley.edu/)
    - プロジェクトの公式ページ
        - 登録してと書かれている
        - ただ結構リンク切れが多い
- [https://opensees.ist.berkeley.edu/wiki/index.php](https://opensees.ist.berkeley.edu/wiki/index.php?title=Main_Page)
    - OpenseesのWiki
    - 左側の`User Documentation`から、ユーザーマニュアルにアクセスできる
- [https://opensees.github.io/OpenSeesDocumentation/](https://opensees.github.io/OpenSeesDocumentation/)
    - Github Pagesで公開されているドキュメント
    - 上記のWikiと内容が異なる？こちらのほうが扱いやすいイメージ
- [https://github.com/OpenSees/OpenSees](https://github.com/OpenSees/OpenSees)
    - Githubのリポジトリ
    - ソースコードが公開されている
    - 現時点(2024/07/06)でのバージョンは`3.6.0`
- [https://openseespydoc.readthedocs.io/en/latest/](https://openseespydoc.readthedocs.io/en/latest/)
    - OpenseesPyのドキュメント
    - 作成者は[Mingjie ZHU氏](https://github.com/zhuminjie)
- [https://github.com/zhuminjie/OpenSeesPy](https://github.com/zhuminjie/OpenSeesPy)
    - 同じ作成者のMingjie ZHU氏が作成したOpenseesPyのリポジトリ
    - こちらもソースコードが公開されているが、厳密には同じバージョンではない？
        - 現時点(2024/07/06)でのバージョンは`3.6.0.3`となっている
    - 現時点(2024/07/06)で本家`OpenSees`と複数のContributerが被っており、Contributionも活発であるので、開発中止の可能性は薄いだろう。
        - [OpenseesPyのコントリビューション](https://github.com/zhuminjie/OpenSeesPy/graphs/contributors)
        - [OpenSeesのコントリビューション](https://github.com/OpenSees/OpenSees/graphs/contributors)

### 単位について
- [ここ](https://opensees.berkeley.edu/OpenSees/manuals/usermanual/566.htm)を読むと、単位系については依拠しないと書かれている。
    - Metricであろうが、Imperialであろうが、どちらでも使える
    - ただ一部の材料モデル(例えば[FRPConfinedConcrete02](https://openseespydoc.readthedocs.io/en/latest/src/FRPConfinedConcrete02.html)など)では、単位系に依存するパラメータや、単位系を引数で設定するものがあるので注意

## 2024/07/06

- 小目標1：サンプルコードのわからなかった部分をソースコードから理解
- 小目標2：単一要素の液状化解析を行うコードを作成する

### 不明点

- [参考にしたリンク](https://github.com/zhuminjie/OpenSeesPyDoc/blob/master/pyExamples/PM4Sand_Cyc_Cal.py)
- Line 165: `op.pattern('Plain', 2, 2,'-factor',1.0)`
    - Q1:`-factor`は`'-fact'`ではないか？
    - Q2:`'-fact'`を設定する意味とは？
- `op.setParameter('-val', 0, '-ele', 1, 'FirstCall', '1')`
    - Q1:`FirstCall`は何を指定している？
    - Q2:一番最後の`1`はなんの意味を持つ？
- `op.setParameter('-val', 0.3, '-ele',1, 'poissonRatio', '1')`
    - Q1:一番最後の`'1'`はなんの意味を持つ？
        - しかも`1`ではなく、`'1'`でないといけない
- `op.sp(3, 1, 1.0)`
    - Q1:なぜ3つ目の引数がfloat?
- `SSPquadUP`について
    - Q1:`SSPquadUP`はどのような要素か？
    - Q2:そもそもElementとは何か？

### ソースコードからの理解
- そもそも`OpenSeesPy`のソースコードの構造が分からない。どこを見ればいいのか分からない
    - `pip/openseespy/opensees/__init__.py`を見ると、プラットフォームによって、インポートするモジュールが変わるようになっている
    - もともと`TCL`で書かれたもの
        - `Tool Command Language`の略
            - lammpsでも同じようなものを使ったな... 
                - [ここ](https://docs.lammps.org/Tools.html#building-the-wrapper)を見ると、どうやらlammpsはビルド時にオプションをつけることで、ラッパーを変更できるようだ
                    - すげえなぁ
    - おそらく`SRC`ディレクトリを見ればよさそう
        - ただ、pythonラッパーとの対応がよくわからない
            - pythonで与えれた引数がどのようにTCLに渡されるのかが分からない。
- `SRC/domain/pattern`を見る
    - [ここ](https://github.com/zhuminjie/OpenSeesPy/blob/ac4a48f237374db7eaf2d4cd7406360b1ba670cf/SRC/domain/pattern/TclPatternCommand.cpp#L116)に`Plain`の実装がある
    - [ここ](https://github.com/zhuminjie/OpenSeesPy/blob/ac4a48f237374db7eaf2d4cd7406360b1ba670cf/SRC/domain/pattern/TclPatternCommand.cpp#L120)に該当の情報がある
        - 結局、`'-factor'`でも`'-fact'`でもどちらでもいいらしい
        - 値は`float`に変換されて、変数`fact`に代入される
- `SRC/material/nD/UWmaterials/PM4Sand.cpp`を見る
    - ここにはPM4Sandの実装がある
        - `m_FirstCall`と`m_PostShake`が書かれている
    - [ここ](https://github.com/zhuminjie/OpenSeesPy/blob/ac4a48f237374db7eaf2d4cd7406360b1ba670cf/SRC/material/nD/UWmaterials/PM4Sand.cpp#L725C1-L766C2)には、`setParameter`の実装がある
        - 用意されているのは、`FirstCall`と`PostShake`以外にもいくつかのパラメータがあるが全てではない
        - `FirstCall`と`PostShake`は、`m_FirstCall`と`m_PostShake`に代入される
        - PM4Sandの`initilize`関数は初期応力が定義されている場合とされていない場合で別々のものが用意されている
            - `FirstCall`が0のとき(?、正確にはresponseIDが8のとき)、初期応力が定義されている場合の初期化が行われる。
                - この部分の記述はあいまい。
        - `PostShake`の場合は、現在の応力状態と累積ひずみを考慮した、砂のせん断剛性率と体積弾性係数の値を決定する。

### 単位について
- [ここ](https://opensees.berkeley.edu/OpenSees/manuals/usermanual/566.htm)を読むと、単位系については依拠しないと書かれている。
    - Metricであろうが、Imperialであろうが、どちらでも使える

### 追加の調べ物
- 間隙水圧について
    - [ここ](https://opensees.berkeley.edu/wiki/index.php/SSPquadUP_Element)によると、間隙圧のrecoderは以下のように指定するらしい
        -  `op.recorder('Node','-file', 'CycPP.txt','-time', '-node',1,2,3,4,'-dof', 3, 'vel')`
        - なぜ`vel`で参照するのか？


## 2024/07/04

- 目標：OpenseesPyで、単純せん断試験のシミュレーションを行う

### 現状のコード(UCU_test.py)のざっとした説明
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
        - nDMaterialは、n dimensional materialの略？
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
    - [参考](https://openseespydoc.readthedocs.io/en/latest/src/quad.html)
    - `op.element()`は、要素を定義する関数
    - `quad`は、要素のタイプ。四角形要素を指定
        - 例えば他には`truss`や`beamColumn`などがある
    - `1`は、要素のID
    - `1,2,3,4`は、要素を構成する節点のID
    - `1.0`は、要素の厚さ
    - `PlaneStrain`は、要素のタイプ。平面ひずみを指定
        - 他には`PlaneStress`がある
    - `1`は、nDMaterialで定義した材料のID
    - これ以降はoptionalな変数
        - `0.0`は、surface pressure
        - `rho`は、要素の質量密度
            - `0.0, -9.81`は、constant body forces defined in the isoparametric domain
- `op.timeSeries('Linear', 1)`について
    - `op.timeSeries()`は、TimeSeriesオブジェクトを作成する関数。このオブジェクトは時刻と荷重ファクターを関連付ける。
    - `Linear`は、TimeSeriesのタイプ。線形に増加する荷重ファクターを指定
        - `1`は、TimeSeriesのID
        - `factor`は、荷重ファクターの増加率
        - `tStart`は、TimeSeriesの開始時刻
        - 計算式は$\lambda = f(t) = factor * (t - tStart)$のようになる
    - `Trig`は`Trigonometric`の意味で三角関数の波形を意味する
        - `op.timeSeries('Trig', tag, tStart, tEnd, period, '-factor', factor=1.0, '-shift', shift=0.0, '-zeroShift', zeroShift=0.0)`
        - `tag`は、TimeSeriesのID
        - `tStart`は、TimeSeriesの開始時刻
        - `tEnd`は、TimeSeriesの終了時刻
        - `period`は、周期
        - `factor`は、荷重ファクターの増加率
        - `shift`は、波形の位相シフト
        - `zeroShift`は、波形の位相シフト。こちらは、$\lambda$の値から決める場合に使う
        - 計算式は以下の通り
            - $\lambda = f(t) = factor * sin(2\pi(t - tStart)/period + \phi)$
                - ここで$ \phi = shift - \frac{period}{2\pi} * arcsin(zeroShift/factor) $

- `op.pattern('Plain', 1, 1)`について
    - `op.pattern()`は、LoadPatternオブジェクトを作成する関数。このオブジェクトは、TimeSeriesオブジェクトとLoadPatternオブジェクトを関連付ける。
        - `Plain`は、LoadPatternのタイプ。簡単な荷重パターンを指定。
        - `1`は、LoadPatternのID
        - `1`は、TimeSeriesのID
        - `can contain multiple NodalLoads, ElementalLoads and SP_Constraint objects`←この記述がよくわからない
- `op.load(1, 0.0, -rho * 9.81 * width * height / 4)`について
    - `op.load()`は、節点に荷重を与える関数
    - `1`は、節点のID
    - `0.0`は、荷重のx成分
    - `-rho * 9.81 * width * height / 4`は、荷重のy成分
        - `rho`は、要素の質量密度
        - `9.81`は、重力加速度
        - `width`は、要素の幅
        - `height`は、要素の高さ
        - `/ 4`は、要素の四つの節点に均等に荷重を与えるため
ここからが重要な気がする...
- `op.system('BandGeneral')`
    - `op.system()`は、解析のシステムを設定する関数
        - [参考](https://openseespydoc.readthedocs.io/en/latest/src/system.html)
    - `BandGeneral`は、バンド行列を用いた解法を指定
- `op.numberer('Plain')`
    - [参考](https://openseespydoc.readthedocs.io/en/latest/src/numberer.html)
    - `op.numberer()`は、節点や自由度の番号付けを行う関数
    - `Plain`は、通常の番号付けを指定
- `op.constraints('Plain')`
    - [参考](https://openseespydoc.readthedocs.io/en/latest/src/PlainConstraint.html)
    - `op.constraints()`は、拘束条件を設定する関数
    - `Plain`は、通常の拘束条件を指定
- `op.integrator('Newmark', 0.5, 0.25)`
    - [参考](https://openseespydoc.readthedocs.io/en/latest/src/integrator.html)
    - `op.integrator()`は、積分法を設定する関数
    - `Newmark`は、ニューマーク法を指定
    - `0.5`は、$\gamma$の値
    - `0.25`は、$\beta$の値
- `op.algorithm('Newton')`
    - [参考](https://openseespydoc.readthedocs.io/en/latest/src/algorithm.html)
    - `op.algorithm()`は、解法アルゴリズムを設定する関数
    - `Newton`は、ニュートン・ラプソン法を指定
- `op.analysis('Transient')`
    - [参考](https://openseespydoc.readthedocs.io/en/latest/src/analysis.html)
    - `op.analysis()`は、解析の種類を設定する関数
    - `Transient`は、静的解析ではない、過渡解析を指定。時間ステップは一定。
- `op.recorder('Element', '-file', 'stress_strain.out', '-time', '-ele', 1, 'stress')`
    - [参考](https://openseespydoc.readthedocs.io/en/latest/src/recorder.html)
    - `op.recorder()`は、結果を記録する関数
    - `Element`は、要素の結果を記録
    - `-file`は、ファイル名を指定
    - `stress_strain.out`は、ファイル名
    - `-time`は、時間を記録
    - `-ele`は、要素を指定
    - `1`は、要素のID
    - `stress`は、記録する結果の種類


### 他のサンプルコードを見てみる
- [PM4Sandを用いたpythonスクリプト](https://github.com/zhuminjie/OpenSeesPyDoc/blob/master/pyExamples/PM4Sand_Cyc_Cal.py)
    - 色々参考になる
    - ざっとした構造は以下の通り。**太字**は、初期コードで考慮していなかった部分
        - Line 28から75まで：モデルのパラメータの設定
            - PM4Sandのオプショナルパラメータまでしっかりと設定されているのが印象的。
        - Line 78から86まで：レイリー減衰のパラメータの設定
        - Line 93：op.model()の設定
            - 次元数は2、自由度は3
        - Line 96から119までは接点と境界条件の設定
            - op.fix()でなぜか3次元目までの拘束条件を設定している
                - 3次元目ではなく3自由度目(せん断変形)を初期状態では拘束するため
        - **Line 120：op.equalDOF()で節点3と4の変位を等しくする**
        - Line 128でop.nDMaterial()でPM4Sandの設定
        - **Line 131から134で、op.element()の設定**
            - ここで用いているのは`quad`ではなく、`SSPquadUP`という要素
            - `SSPquad`の拡張型
                - `SSPquad`は、四角形要素の中でも特に平面ひずみを考慮したもの
                    - `SSP`はStablized Single Pointの略
                    - 以下ドキュメントからの引用。
                        >  The SSPquad element is a four-node quadrilateral element using physically stabilized single-point integration (SSP –> Stabilized Single Point). The stabilization incorporates an assumed strain field in which the volumetric dilation and the shear strain associated with the the hourglass modes are zero, resulting in an element which is free from volumetric and shear locking. The elimination of shear locking results in greater coarse mesh accuracy in bending dominated problems, and the elimination of volumetric locking improves accuracy in nearly-incompressible problems. Analysis times are generally faster than corresponding full integration elements. The formulation for this element is identical to the solid phase portion of the SSPquadUP element as described by McGann et al. (2012).
                    - 意訳
                        - SSPquad要素は、4つの節点を有する四辺形要素。この要素は物理的に安定である1点積分を用いている。この安定化は、アワーガラスモードに関連するダイレーションとせん断ひずみが0であるひずみ条件下を組み込み、体積およびせん断ロッキングを発生させない。せん断ロッキングをなくすことによって、曲げ支配問題において粗いメッシュの精度が向上し、体積ロッキングをなくすことによって、準非圧縮問題において精度が向上する。解析時間は通常、対応する完全積分要素よりも短い。この要素の公式は、McGannらによって説明されたSSPquadUP要素の固相部分と同一。
            - それでは`SSPquadUP`は？
                - 飽和された多孔質体の動的な平面ひずみ解析に利用される要素
                - u-p formulationを用いている
                - Biotならびに、それを拡張したZienkiewicz and Shiomiの論文に基づく
                - TODO:ドキュメントと関連論文を読む
        - Line 135から140はRecorderの設定
        - Line 141から149は解析の設定
            - 初期コードと若干異なる
            - `op.constraints('Transformation')`は、拘束条件を設定
                - `Note`の欄には、拘束条件について注意が必要と書かれている。が、詳細はまだ理解できていない
                    - [Noteへのリンク](https://openseespydoc.readthedocs.io/en/latest/src/TransformationMethod.html)
            - `op.test('NormDispIncr', 1.0e-5, 35, 1)`は、収束条件を設定
                - `NormDispIncr`は、変位の増分のノルムを収束条件として指定
                - `1.0e-5`は、収束条件の許容誤差
                - `35`は、最大反復回数
                - `1`は、PrintFlagで、以下のような仕様になっている
                    - 0: 何も出力しない
                    - 1: test()が呼び出されるたびにノルムに関する情報を出力
                    - 2: 成功したテストの最後にノルムと反復回数に関する情報を出力
                    - 4: 各ステップでノルムと、$\Delta U$と$R(U)$のベクトルを出力
                    - 5: 反復回数が最大反復回数に達した場合、エラーメッセージを出力して成功したテストを返す
            - `op.algorithm('Newton')`は、解法アルゴリズムを設定
            - `op.numberer('RCM')`は、節点や自由度の番号付けを行う
                - `RCM`は、Reverse Cuthill-McKee法を指定
                    - [Wikiへのリンク](https://ja.wikipedia.org/wiki/%E3%82%AB%E3%83%83%E3%83%88%E3%83%92%E3%83%AB%E3%83%BB%E3%83%9E%E3%82%AD%E3%83%BC%E6%B3%95)
                - > 対称なパターンを持つ疎行列を帯幅（英語版）の小さい帯行列（英語版）の形に並べ替えるアルゴリズム
            - `op.system('FullGeneral')`は、解析のシステムを設定
                - `FullGeneral`は、一般的なフル行列を用いた解法を指定
                - 公式Documentationではではあまり推奨されていない
                    - メモリの使用量が多いため
                - 逆に言えばメモリ使用量の削減手法があるということ
            - `op.integrator('Newmark', 5.0/6.0, 4.0/9.0)`は、積分法を設定
            - `op.rayleigh(a1, a0, 0.0, 0.0)`は、レイリー減衰の設定
                - ここでは、$a_1$と$a_0$のみを設定
                - レイリー減衰の計算式は以下の通り
                    - Dは指定された剛性と質量比例の減衰行列
                    - $D = \alpha_M M + \beta_K K + \beta_Kinit K_init + \beta_Kcomm K_comm$
                        - $M$は質量行列
                        - $K$は現時点での剛性行列
                        - $K_init$は初期剛性行列
                        - $K_comm$はcommitted stiffness matrix
        - Line 154から167はLoading Patternの設定
            - `op.timeSeries('Path', 1, '-values', 0, 1, 1, '-time', 0.0, 100.0, 1.0e10)`は、TimeSeriesの設定
                - `Path`は、時刻とLoadFactorの関係性を2つの数字の組、あるいはそれを含んだリストで指定する
                    - こっちのほうがわかりやすい...
                - ファイルからのロードも可能
                    - 実波形のインポートも可能！
                - 指定した時刻におけるLoading Factorが存在しない場合は、内挿値を使用
                - この場合の設定だと、時刻0から100までの間、Loading Factorが0から1まで線形に増加し、その後1.0e10の時間まで1が維持される。
                    - 繰り返し載荷ではない？
                        - 違うわ、これは鉛直載荷のための設定だ
            - `op.pattern("Plain", 1, 1, '-factor',1.0)`は、LoadPatternの設定
            - `op.load(3, 0.0, pNode, 0.0)`は、節点3に荷重を与える
            - `op.updateMaterialStage('-material', 1, '-stage', 0)`は、材料のステージを更新
                - ステージって何？
                - [本家のHP](https://opensees.berkeley.edu/wiki/index.php/UpdateMaterialStage)にかかれていた
                - `op.nDMaterial()`で設定した材料パラメータ(構成則)は`stage = 0`のときには適用されない。
                    - 初期圧密、あるいは繰り返しせん断前の状態を再現するためのもの
                - `0`：線形弾性。デフォルトではこれだから、実は明示する必要はない。
                - `1`：塑性
                - `2`：初期有効応力に依存した弾性
            - `op.analyze(100,1.0)`は、解析を行う
                - `100`は、解析ステップ数
                - `1.0`は、時間ステップ
            - `vDisp = op.nodeDisp(3,2)`は、節点3のy方向の変位を取得
            - `b = op.eleResponse(1, 'stress')`は、要素1の応力を取得
            - `op.timeSeries('Path', 2, '-values', 1.0, 1.0, 1.0, '-time', 100.0, 80000.0, 1.0e10, '-factor', 1.0)`は、繰り返しせん断用のTimeSeriesの設定
                - こちらの設定は、時刻100からずっと1.0のLoading Factorを維持する
            - `op.pattern('Plain', 2, 2,'-factor',1.0)`は、LoadPatternの設定
                - ドキュメントを読むと、`'-factor'`は`'-fact'`ではないか？
                - ただ、`'-fact'`を設定する意味がわからない
            - `op.sp(3, 2, vDisp)`は、節点3の自由度2(y方向?)の変位をvDispで固定する
                - なぜ応力でなく変位固定なのか？
                - `sp`はsingle point constraintsの意味
        - Line 169から172で非排水へ変更
            - `op.remove('sp', i+1, 3)`
                - 3は3自由度目なので、せん断変形？
                - ようするにすべてのノードでせん断変形を可能にする？
                - `op.fix(1, 1, 1, 1)`で`op.sp(1, 3, 0)`状態になっているため、このコマンドで拘束を解かないといけない
        - Line 175から178で非排水状態にして要素が安定化するまで待つ
            - 安定化したのち、せん断応力を取得
        - Line 180で`material`の`stage`をスイッチ
        - Line 191でパラメータの値を更新？
            - コメントに書かれている内容を見ると、`Element`は内部のパラメータとして`FirstCall`と`Postshake`が用意されており、PM4SiltやPM4SandはそれをFlagとして、材料モデルの`A_do`と`z_max`の値を初期化?するよう。
            - > `A_do : Optional, Dilatancy parameter, will be computed at the time of initialization if input value is negative`
            - > `z_max : Optional, Fabric-dilatancy tensor parameter`

                - [PM4SiltのWiki](https://openseespydoc.readthedocs.io/en/latest/src/PM4Silt.html)
        - Line 193から199では材料モデルを変更後、もう一度安定化するまで待つ
            - `op.setParameter('-val', 0.3, '-ele',1, 'poissonRatio', '1')`
                - 要素番号1の`poissonRatio`の値を0.3に書き換えるという意味。
                    - 一番最後の`1`はなんの意味を持つ？
        - Line 206から繰り返し載荷を開始
            - `op.timeSeries('Path', 3,'-values', hDisp, controlDisp, controlDisp, '-time', cur_time, time_change, 1.0e10, '-factor', 1.0)`
                - 線形増加？しかもひずみ速度一定の条件
            - `op.pattern('Plain', 3, 3, '-fact', 1.0)`
                - `-fact`ってなんだっけ？
            - `op.sp(3, 1, 1.0)`
                - 節点3のx方向の変位を固定
                    - なぜ3つ目の引数がfloat?
            - `while`文で規定のCSRに相当するせん断応力まで到達するまで解析を1ステップずつ進める
            - 荷重が反転する際には`op.remove()`で、loading pattern、timeSeries、spを一旦削除
                - spは削除しなくてもよいのでは？
            - 以下荷重反転後は上記の繰り返し
            

                        

