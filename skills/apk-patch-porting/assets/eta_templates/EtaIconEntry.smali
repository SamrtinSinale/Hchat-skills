.class public final Lh/Hchat/hooks/items/customnotify/EtaIconEntry;
.super Ljava/lang/Object;


# static fields
.field public static attached:Z


# direct methods
.method public constructor <init>()V
    .locals 0

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static addNotifyIconRows(L{{COMPOSE}};)V
    .locals 6

    :try_start_0
    new-instance v0, L{{WRAPPER}};

    new-instance v1, Lh/Hchat/hooks/items/customnotify/EtaIconPickClick;

    invoke-direct {v1}, Lh/Hchat/hooks/items/customnotify/EtaIconPickClick;-><init>()V

    const/4 v2, 0x4

    invoke-direct {v0, v1, v2}, L{{WRAPPER}};-><init>(L{{LAMBDA}};I)V

    invoke-virtual {p0, v0}, L{{COMPOSE}};->{{COMPOSE_PUSH}}(Ljava/lang/Object;)V

    check-cast v0, L{{ROWCLICK}};

    const-string v1, "\u81ea\u5b9a\u4e49\u56fe\u6807"

    const-string v2, "\u9009\u62e9\u56fe\u7247\u4f5c\u4e3a\u901a\u77e5\u5c0f\u56fe\u6807"

    const/4 v3, 0x6

    invoke-static {v1, v2, v0, p0, v3}, L{{SETTINGS_UI}};->a(Ljava/lang/String;Ljava/lang/String;L{{ROWCLICK}};L{{COMPOSE}};I)V

    new-instance v0, L{{WRAPPER}};

    new-instance v1, Lh/Hchat/hooks/items/customnotify/EtaIconResetClick;

    invoke-direct {v1}, Lh/Hchat/hooks/items/customnotify/EtaIconResetClick;-><init>()V

    const/4 v2, 0x4

    invoke-direct {v0, v1, v2}, L{{WRAPPER}};-><init>(L{{LAMBDA}};I)V

    invoke-virtual {p0, v0}, L{{COMPOSE}};->{{COMPOSE_PUSH}}(Ljava/lang/Object;)V

    check-cast v0, L{{ROWCLICK}};

    const-string v1, "\u6062\u590d\u9ed8\u8ba4\u56fe\u6807"

    const-string v2, "\u6e05\u9664\u81ea\u5b9a\u4e49\u56fe\u6807\uff0c\u4f7f\u7528\u5fae\u4fe1\u9ed8\u8ba4\u56fe\u6807"

    invoke-static {v1, v2, v0, p0, v3}, L{{SETTINGS_UI}};->a(Ljava/lang/String;Ljava/lang/String;L{{ROWCLICK}};L{{COMPOSE}};I)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :catch_0
    return-void
.end method

.method public static attach(Landroid/view/ViewGroup;)V
    .locals 10

    :try_start_0
    if-nez p0, :cond_0

    return-void

    :cond_0
    sget-boolean v0, Lh/Hchat/hooks/items/customnotify/EtaIconEntry;->attached:Z

    if-eqz v0, :cond_1

    return-void

    :cond_1
    const/4 v0, 0x1

    sput-boolean v0, Lh/Hchat/hooks/items/customnotify/EtaIconEntry;->attached:Z

    invoke-virtual {p0}, Landroid/view/ViewGroup;->getContext()Landroid/content/Context;

    move-result-object v0

    if-nez v0, :cond_2

    return-void

    :cond_2
    new-instance v1, Landroid/widget/LinearLayout;

    invoke-direct {v1, v0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    const/4 v2, 0x1

    invoke-virtual {v1, v2}, Landroid/widget/LinearLayout;->setOrientation(I)V

    const/16 v2, 0x28

    const/16 v3, 0x14

    const/16 v4, 0x28

    const/16 v5, 0x14

    invoke-virtual {v1, v2, v3, v4, v5}, Landroid/view/View;->setPadding(IIII)V

    new-instance v2, Landroid/widget/TextView;

    invoke-direct {v2, v0}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    const-string v3, "\u81ea\u5b9a\u4e49\u901a\u77e5\u56fe\u6807"

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    const/high16 v3, 0x41900000    # 18.0f

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setTextSize(F)V

    new-instance v3, Lh/Hchat/hooks/items/customnotify/EtaIconEntry$1;

    invoke-direct {v3}, Lh/Hchat/hooks/items/customnotify/EtaIconEntry$1;-><init>()V

    invoke-virtual {v2, v3}, Landroid/view/View;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    invoke-virtual {v1, v2}, Landroid/view/ViewGroup;->addView(Landroid/view/View;)V

    new-instance v2, Landroid/widget/TextView;

    invoke-direct {v2, v0}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    const-string v3, "\u6062\u590d\u9ed8\u8ba4\u56fe\u6807"

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    const/high16 v3, 0x41900000    # 18.0f

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setTextSize(F)V

    new-instance v3, Lh/Hchat/hooks/items/customnotify/EtaIconEntry$2;

    invoke-direct {v3}, Lh/Hchat/hooks/items/customnotify/EtaIconEntry$2;-><init>()V

    invoke-virtual {v2, v3}, Landroid/view/View;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    invoke-virtual {v1, v2}, Landroid/view/ViewGroup;->addView(Landroid/view/View;)V

    new-instance v2, Landroid/widget/FrameLayout$LayoutParams;

    const/4 v3, -0x2

    const/4 v4, -0x2

    invoke-direct {v2, v3, v4}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    const/16 v3, 0x50

    iput v3, v2, Landroid/widget/FrameLayout$LayoutParams;->gravity:I

    const/16 v3, 0xa

    iput v3, v2, Landroid/widget/FrameLayout$LayoutParams;->bottomMargin:I

    invoke-virtual {p0, v1, v2}, Landroid/view/ViewGroup;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_0

    :catch_0
    move-exception v0

    invoke-static {v0}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->log(Ljava/lang/Throwable;)V

    :goto_0
    return-void
.end method

.method public static pick()V
    .locals 4

    :try_start_0
    invoke-static {}, Lh/Hchat/hooks/items/customnotify/EtaIconHook;->install()V

    invoke-static {}, Lh/Hchat/hooks/items/customnotify/EtaIconHook;->current()Landroid/app/Activity;

    move-result-object v0

    if-eqz v0, :cond_0

    new-instance v1, Landroid/content/Intent;

    const-string v2, "android.intent.action.GET_CONTENT"

    invoke-direct {v1, v2}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    const-string v2, "image/*"

    invoke-virtual {v1, v2}, Landroid/content/Intent;->setType(Ljava/lang/String;)Landroid/content/Intent;

    const/16 v2, 0x2768

    invoke-virtual {v0, v1, v2}, Landroid/app/Activity;->startActivityForResult(Landroid/content/Intent;I)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :catch_0
    :cond_0
    return-void
.end method

.method public static addRows(L{{COMPOSE}};)V
    .locals 5

    :try_start_0
    new-instance v0, Lh/Hchat/hooks/items/customnotify/EtaIconRowClick;

    const/4 v1, 0x0

    invoke-direct {v0, v1}, Lh/Hchat/hooks/items/customnotify/EtaIconRowClick;-><init>(I)V

    const-string v1, "\u81ea\u5b9a\u4e49\u56fe\u6807"

    const-string v2, "\u9009\u62e9\u56fe\u7247\u4f5c\u4e3a\u901a\u77e5\u5c0f\u56fe\u6807"

    const/4 v3, 0x6

    invoke-static {v1, v2, v0, p0, v3}, L{{SETTINGS_UI}};->a(Ljava/lang/String;Ljava/lang/String;L{{ROWCLICK}};L{{COMPOSE}};I)V

    new-instance v0, Lh/Hchat/hooks/items/customnotify/EtaIconRowClick;

    const/4 v1, 0x1

    invoke-direct {v0, v1}, Lh/Hchat/hooks/items/customnotify/EtaIconRowClick;-><init>(I)V

    const-string v1, "\u6062\u590d\u9ed8\u8ba4\u56fe\u6807"

    const-string v2, "\u6e05\u9664\u81ea\u5b9a\u4e49\u56fe\u6807\uff0c\u4f7f\u7528\u5fae\u4fe1\u9ed8\u8ba4\u56fe\u6807"

    const/4 v3, 0x6

    invoke-static {v1, v2, v0, p0, v3}, L{{SETTINGS_UI}};->a(Ljava/lang/String;Ljava/lang/String;L{{ROWCLICK}};L{{COMPOSE}};I)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    return-void

    :catch_0
    move-exception v0

    invoke-static {v0}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->log(Ljava/lang/Throwable;)V

    return-void
.end method
