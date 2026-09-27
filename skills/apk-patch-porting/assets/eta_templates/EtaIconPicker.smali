.class public final Lh/Hchat/hooks/items/customnotify/EtaIconPicker;
.super Ljava/lang/Object;


# direct methods
.method public constructor <init>()V
    .locals 0

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static launch()V
    .locals 2

    :try_start_0
    invoke-static {}, Lh/Hchat/hooks/items/customnotify/EtaIconHook;->install()V

    invoke-static {}, Lh/Hchat/hooks/items/customnotify/EtaIconHook;->current()Landroid/app/Activity;

    move-result-object v0

    if-eqz v0, :cond_0

    invoke-static {v0}, Lh/Hchat/hooks/items/customnotify/EtaIconPicker;->startPick(Landroid/app/Activity;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :catch_0
    :cond_0
    return-void
.end method

.method public static startPick(Landroid/app/Activity;)V
    .locals 4

    new-instance v0, Landroid/content/Intent;

    const-string v1, "android.intent.action.GET_CONTENT"

    invoke-direct {v0, v1}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    const-string v1, "image/*"

    invoke-virtual {v0, v1}, Landroid/content/Intent;->setType(Ljava/lang/String;)Landroid/content/Intent;

    const/16 v1, 0x2768

    invoke-virtual {p0, v0, v1}, Landroid/app/Activity;->startActivityForResult(Landroid/content/Intent;I)V

    return-void
.end method

.method public static toActivity(Landroid/content/Context;)Landroid/app/Activity;
    .locals 3

    const/4 v2, 0x0

    move-object v0, p0

    :goto_0
    if-nez v0, :cond_0

    return-object v2

    :cond_0
    instance-of v1, v0, Landroid/app/Activity;

    if-eqz v1, :cond_1

    check-cast v0, Landroid/app/Activity;

    return-object v0

    :cond_1
    instance-of v1, v0, Landroid/content/ContextWrapper;

    if-eqz v1, :cond_2

    check-cast v0, Landroid/content/ContextWrapper;

    invoke-virtual {v0}, Landroid/content/ContextWrapper;->getBaseContext()Landroid/content/Context;

    move-result-object v0

    goto :goto_0

    :cond_2
    return-object v2
.end method


# virtual methods
.method public final invoke()Ljava/lang/Object;
    .locals 5

    const/4 v4, 0x0

    :try_start_0
    const-string v0, "picker invoked"

    invoke-static {v0}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->logStr(Ljava/lang/String;)V

    invoke-static {}, Lh/Hchat/hooks/items/customnotify/EtaIconHook;->install()V

    invoke-static {}, Lh/Hchat/hooks/items/customnotify/EtaIconHook;->current()Landroid/app/Activity;

    move-result-object v1

    if-nez v1, :cond_0

    sget-object v1, Lh/Hchat/hooks/items/customnotify/EtaIconHook;->lastContext:Landroid/content/Context;

    invoke-static {v1}, Lh/Hchat/hooks/items/customnotify/EtaIconPicker;->toActivity(Landroid/content/Context;)Landroid/app/Activity;

    move-result-object v1

    :cond_0
    if-eqz v1, :cond_1

    const-string v0, "activity found, start pick"

    invoke-static {v0}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->logStr(Ljava/lang/String;)V

    invoke-static {v1}, Lh/Hchat/hooks/items/customnotify/EtaIconPicker;->startPick(Landroid/app/Activity;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_0

    :catch_0
    move-exception v0

    invoke-static {v0}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->log(Ljava/lang/Throwable;)V

    :cond_1
    const-string v0, "no activity found"

    invoke-static {v0}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->logStr(Ljava/lang/String;)V

    :goto_0
    invoke-static {v4}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v0

    return-object v0
.end method
