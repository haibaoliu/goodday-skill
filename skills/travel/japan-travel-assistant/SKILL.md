---
name: japan-travel-assistant
description: 日本旅行助手 —— 中日双语翻译桥（语音→中文→日文→给当地人看→日文回复→翻译中文）、东京交通导航、菜单标识翻译、带娃出行攻略、紧急联络。覆盖点餐、问路、购物、看病、求助等全部旅行场景。当用户在日本旅行、需要中日翻译、或提及日本/东京/日语相关时自动激活。
version: 1.0.0
tags: [japan, travel, translation, tokyo, japanese, kids]
---

# 日本旅行助手

## 核心模式：中日翻译桥

这是最重要的功能。在旅行中充当**实时双向翻译桥**：

### 模式 A：你要对日本人说话
```
你（语音/文字中文）→ wawa 翻译成日文 → 你把手机屏幕给对方看
```
- 日文翻译要加粗、加大、单独一行，方便直接展示
- 日文下方可选附罗马字读音（对方看不懂汉字时备用）
- 语气要有礼貌（です・ます体），你是游客要有礼貌

### 模式 B：日本人回复你
```
日本人输入日文 → wawa 翻译成中文 → 你读懂
```
- 中文翻译要自然、口语化
- 如果对方说了敬语/方言/缩略语，标注一下

### 模式 C：拍照翻译
```
拍菜单/路牌/标识/说明书 → wawa 识别日文 → 翻译中文 + 解释含义
```

---

## 常用日语速查（按场景）

### 🍜 餐厅点餐
| 中文 | 日文 | 读音 |
|------|------|------|
| 这个是什么？ | これは何ですか？ | Kore wa nan desu ka? |
| 请给我这个 | これをください | Kore o kudasai |
| 有中文/英文菜单吗？ | 中国語/英語のメニューはありますか？ | Chuugokugo/Eigo no menyuu wa arimasu ka? |
| 不要辣 | 辛くしないでください | Karaku shinaide kudasai |
| 孩子可以吃吗？ | 子供でも食べられますか？ | Kodomo demo taberaremasu ka? |
| 有什么推荐？ | おすすめは何ですか？ | Osusume wa nan desu ka? |
| 结账 | お会計お願いします | O-kaikei onegai shimasu |
| 分开付 | 別々でお願いします | Betsubetsu de onegai shimasu |
| 过敏（花生/虾/鸡蛋/牛奶） | アレルギー（ピーナッツ/エビ/卵/牛乳） | Arerugii (piinattsu/ebi/tamago/gyuunyuu) |
| 带走 | 持ち帰りでお願いします | Mochikaeri de onegai shimasu |
| 在这吃 | ここで食べます | Koko de tabemasu |

### 🚃 交通问路
| 中文 | 日文 | 读音 |
|------|------|------|
| 怎么去…？ | …までどうやって行きますか？ | ...made dou yatte ikimasu ka? |
| 这个站怎么走？ | この駅はどう行けばいいですか？ | Kono eki wa dou ikeba ii desu ka? |
| 去…坐哪条线？ | …までは何線ですか？ | ...made wa nan-sen desu ka? |
| 这是去…的车吗？ | これは…行きですか？ | Kore wa ... yuki desu ka? |
| 下一站是…吗？ | 次の駅は…ですか？ | Tsugi no eki wa ... desu ka? |
| 在哪里换乘？ | 乗り換えはどこですか？ | Norikae wa doko desu ka? |
| 末班车几点？ | 終電は何時ですか？ | Shuuden wa nan-ji desu ka? |
| 西瓜卡在哪充值？ | Suicaはどこでチャージできますか？ | Suica wa doko de chaaji dekimasu ka? |
| 一日券在哪买？ | 一日乗車券はどこで買えますか？ | Ichinichi joushaken wa doko de kaemasu ka? |
| 出口是哪个？ | 出口はどれですか？ | Deguchi wa dore desu ka? |

### 🛍️ 购物
| 中文 | 日文 | 读音 |
|------|------|------|
| 多少钱？ | いくらですか？ | Ikura desu ka? |
| 可以免税吗？ | 免税できますか？ | Menzei dekimasu ka? |
| 请给我护照 | パスポートをお願いします | Pasupooto o onegai shimasu |
| 可以试穿吗？ | 試着してもいいですか？ | Shichaku shite mo ii desu ka? |
| 有别的颜色/尺寸吗？ | 他の色/サイズはありますか？ | Hoka no iro/saizu wa arimasu ka? |
| 能便宜一点吗？ | もう少し安くなりますか？ | Mou sukoshi yasuku narimasu ka? |
| 刷卡可以吗？ | カードは使えますか？ | Kaado wa tsukaemasu ka? |
| 支付宝/微信可以用吗？ | アリペイ/WeChatペイは使えますか？ | Aripei/WeChat pei wa tsukaemasu ka? |
| 请给我收据 | レシートをください | Reshiito o kudasai |
| 只要这个 | これだけで大丈夫です | Kore dake de daijoubu desu |

### 🏥 医疗/紧急
| 中文 | 日文 | 读音 |
|------|------|------|
| 请帮我叫医生 | 医者を呼んでください | Isha o yonde kudasai |
| 孩子发烧了 | 子供が熱を出しました | Kodomo ga netsu o dashimashita |
| 最近的医院在哪？ | 一番近い病院はどこですか？ | Ichiban chikai byouin wa doko desu ka? |
| 会说中文的医生？ | 中国語が話せる医者はいますか？ | Chuugokugo ga hanaseru isha wa imasu ka? |
| 头疼/肚子疼 | 頭が痛い/お腹が痛い | Atama ga itai / Onaka ga itai |
| 有药吗？ | 薬はありますか？ | Kusuri wa arimasu ka? |
| 请帮我 | 助けてください | Tasukete kudasai |
| 报警！ | 警察を呼んでください！ | Keisatsu o yonde kudasai! |
| 大使馆在哪？ | 大使館はどこですか？ | Taishikan wa doko desu ka? |

### 👋 日常礼仪
| 中文 | 日文 | 读音 |
|------|------|------|
| 谢谢 | ありがとうございます | Arigatou gozaimasu |
| 不好意思/打扰了 | すみません | Sumimasen |
| 对不起 | ごめんなさい | Gomen nasai |
| 好的/知道了 | わかりました | Wakarimashita |
| 没关系 | 大丈夫です | Daijoubu desu |
| 我不会说日语 | 日本語が話せません | Nihongo ga hanasemasen |
| 请说慢一点 | ゆっくり話してください | Yukkuri hanashite kudasai |
| 能用翻译 app 吗？ | 翻訳アプリを使ってもいいですか？ | Honyaku apuri o tsukatte mo ii desu ka? |
| 厕所在哪？ | トイレはどこですか？ | Toire wa doko desu ka? |
| 有 Wi-Fi 吗？ | Wi-Fiはありますか？ | Wi-Fi wa arimasu ka? |

---

## 🗼 东京交通速查

### Suica / Pasmo（交通卡）
- 苹果手机：Wallet 直接添加 Suica，银联/信用卡充值
- 实体卡：JR 站自动售票机购买，押金 500 日元
- 儿童（6-12岁）：买「こども Suica」，半价

### 主要线路
| 线路 | 颜色 | 覆盖 |
|------|------|------|
| JR 山手线 Yamanote | 黄绿 | 环线：东京站、涩谷、新宿、池袋、上野 |
| 东京 Metro 银座线 | 橙 | 涩谷↔浅草 |
| 东京 Metro 丸之内线 | 红 | 新宿↔东京站↔池袋 |
| 都营浅草线 | 玫红 | 直通成田/羽田机场 |

### 带孩子坐地铁
- 学龄前免费，小学生半价
- 每个车站都有电梯（找「エレベーター」标识）
- 女性专用车厢（早高峰，找粉色标识）
- 推婴儿车可上任何车厢

---

## 🧒 亲子游推荐

### 必去
| 地点 | 预算 | 半天/全天 |
|------|------|----------|
| 上野动物园 | ¥600（小学生免费） | 半天 |
| 台场 LEGOLAND Discovery Center | ¥2,800 | 半天 |
| 日本科学未来馆（台场） | ¥630 | 半天 |
| 迪士尼乐园/海洋 | ¥7,900-9,400 | 全天 |
| Sanrio Puroland（多摩） | ¥3,800 | 全天 |
| 藤子·F·不二雄博物馆（川崎） | ¥1,000 | 半天 |
| 国立科学博物馆（上野） | ¥630 | 半天 |

### 免费/便宜
- 皇居外苑（草地跑）
- 代代木公园
- 井之头恩赐公园（吉祥寺）
- 东京都厅展望台（免费俯瞰东京）

### 亲子餐厅
- 很多餐厅有「お子様ランチ」（儿童套餐），约 ¥500-800
- 家庭餐厅（ガスト Gusto / サイゼリヤ Saizeriya / デニーズ Denny's）随时有儿童菜单
- 回转寿司（くら寿司 / スシロー）孩子爱看传送带

---

## ⚠️ 紧急联络

| 事项 | 号码 |
|------|------|
| 报警 | 110 |
| 急救/消防 | 119 |
| 中国驻日大使馆 | 03-3403-3388 |
| 东京都医疗信息服务（多语言） | 03-5285-8181 |
| 日本旅游热线（24h 多语言） | 050-3816-2787 |

### 大使馆地址
中国驻日本大使館：〒106-0046 東京都港区元麻布3-4-33

---

## 📝 文化须知

- **靠左走**：东京扶梯站左边，右边是急行道（大阪相反）
- **现金**：很多老店只收现金，备 3-5 万日元现金
- **垃圾**：街上几乎没垃圾桶！随身带垃圾袋
- **安静**：地铁里不要打电话，设静音
- **厕纸**：直接冲走，不要扔垃圾桶
- **脱鞋**：进餐厅榻榻米区/寺庙/一些店要脱鞋
- **小费**：不需要！给反而尴尬
- **排队**：日本人极其守秩序，插队会被侧目
- **温泉**：有纹身可能被拒，先确认

---

## 🔧 翻译桥使用指南

### 当用户语音输入时
1. 如果收到语音消息，说明已自动转文字（STT）
2. 判断是中文还是日文
3. 中文 → 翻译日文，用 `**日文**` 加粗格式，直接给对方看
4. 日文 → 翻译中文，自然口语化

### 翻译格式
```
🗣️ 你可以给对方看：

**日文翻译**

（读音：romaji）

---
如果对方回复日文，截图或打字发给我，我翻译成中文。
```

### 注意事项
- 翻译要自然，不要逐字直译
- 用です・ます体（礼貌体），不要用简体（タメ口）
- 如果你是女性，用稍微柔和的表达（わ、ね、かしら 等女性语尾适中使用）
- 保持简洁——对方没耐心看长篇大论
