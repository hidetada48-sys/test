**デザイントーン**
  google_material_design_style:
  concept:
    core_philosophy: "Physical World Emulation (Paper & Ink)"
    keywords: ["Flat", "Clean", "Intuitive", "Hierarchy"]

  color_system:
    brand_colors:
      google_blue:   "#4285F4" # Primary Action, Links, Trust
      google_red:    "#DB4437" # Alerts, Errors, Attention
      google_yellow: "#F4B400" # Warnings, Highlights
      google_green:  "#0F9D58" # Success, Completion
    text_colors:
      primary:       "#202124" # High emphasis (Headings) - Google Grey 900
      secondary:     "#5F6368" # Medium emphasis (Body) - Google Grey 700
      disabled:      "#BDC1C6" # Inactive - Google Grey 400
    background_colors:
      surface:       "#FFFFFF" # Card surface
      background:    "#F8F9FA" # App background - Google Grey 50

  typography:
    font_family:
      english: "Roboto, Open Sans, Product Sans"
      japanese: "Google Noto Sans JP, Meiryo"
    hierarchy_rules:
      slide_title:
        weight: "Bold"
        size_ratio: 2.5 # Relative to body text
        color: "#202124"
      body_text:
        weight: "Regular"
        size_ratio: 1.0
        color: "#5F6368"
        line_height: 1.5

  components:
    cards:
      background: "#FFFFFF"
      border_radius: "8px" # Slight curve, not a perfect square
      padding: "24px"
    elevation_shadows:
      # Material Design uses shadows to convey depth (Z-axis)
      level_1:
        css_value: "0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)"
        usage: "Card default state"
      level_2:
        css_value: "0 1px 2px 0 rgba(60,64,67,0.3), 0 2px 6px 2px rgba(60,64,67,0.15)"
        usage: "Hover state"

  iconography:
    style: "Material Symbols"
    type: ["Filled", "Outlined"] # Choose one and allow consistency
    characteristics: ["Geometric", "Simple", "No 3D effects"]

  thumbnail_rules:
    mobile_x_thumbnail_priority:
      viewing_context: "スマートフォンのXタイムラインで最初に見られることを前提に設計する"
      design_priority: ["瞬間的な可読性", "主題の即時理解", "視線停止の強さ"]
      success_condition: "縮小表示でもメインタイトルが一瞬で読め、テーマが即時に理解できること"

    information_density:
      max_core_message: 1
      max_major_elements: 3
      emphasize: ["タイトル", "価値", "流れ"]
      prohibit: ["小さな注釈", "長い説明文", "細かい補足", "実装ポイントの過剰記載", "装飾目的だけの小要素"]

    typography_for_thumbnail:
      main_title_position: "左上起点"
      main_title_weight: "Bold"
      main_title_layout: "2段または3段で構成し、重要語句を独立行にして強い階層を作る"
      subcopy_rule: "短く圧縮し、1行から2行以内で処理する"
      hierarchy_order: ["メインタイトル", "強調語", "サブコピー", "補助ラベル"]

    layout_principles:
      white_base_rule: "白ベースを使用しても、余白過多で軽く見える画面にしない"
      structural_anchor: "Google Blueを軸にした太めの面・帯・支柱・ベースラインのいずれかで画面全体を支える"
      composition_rule: "要素は散らさず、1本の太いフローまたは1つの強い構図軸で整理する"
      avoid: ["プレゼン資料風の均等配置", "説明図に見える弱い並列配置", "軽く見える余白の使い方"]
      recommend: ["非対称寄りの視線誘導", "主役が明確な構図", "面で支えるレイアウト"]

    cards_and_icons:
      card_rule: "カードは多用せず、少数で大きく、役割がひと目で分かる単位に絞る"
      icon_rule: "アイコンは飾りではなく、意味の塊を瞬時に伝える視覚記号として使う"
      icon_limit: "主要アイコンは3要素以内を基本とする"
      service_priority_rule: "Google Drive、Discord、Xなど複数サービスがある場合も、主役と脇役を分けて同格に見せない"

    quality_bar:
      target_impression: ["知的", "端的", "プロフェッショナル", "強い", "整理されている"]
      avoid_impression: ["軽い", "素人っぽい", "説明くさい", "情報過多", "サムネとして弱い"]
      final_check: ["スマホ縮小時のタイトル可読性", "主題の即時理解", "不要情報の有無", "視線が止まる強さ"]
      positioning: "図解ではなく、SNS上でクリックを生むキービジュアルとして成立させる"
