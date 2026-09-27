.class public final Lh/Hchat/hooks/items/customnotify/EtaIconStore;
.super Ljava/lang/Object;


# static fields
.field public static final PATH:Ljava/lang/String; = "/data/data/com.tencent.mm/cache/eta_notify_icon.png"

.field public static final REQ:I = 0x2768

.field public static ctx:Landroid/content/Context;


# direct methods
.method public constructor <init>()V
    .locals 0

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static addPickAction(Landroid/app/Notification$Builder;)V
    .locals 5

    :try_start_0
    sget-object v0, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->ctx:Landroid/content/Context;

    if-eqz v0, :cond_0

    new-instance v1, Landroid/content/Intent;

    const-string v2, "h.Hchat.action.CUSTOM_NOTIFICATION_PICK_ICON"

    invoke-direct {v1, v2}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    invoke-virtual {v0}, Landroid/content/Context;->getPackageName()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Landroid/content/Intent;->setPackage(Ljava/lang/String;)Landroid/content/Intent;

    const/16 v3, 0x2769

    const/high16 v2, 0xc000000

    invoke-static {v0, v3, v1, v2}, Landroid/app/PendingIntent;->getBroadcast(Landroid/content/Context;ILandroid/content/Intent;I)Landroid/app/PendingIntent;

    move-result-object v0

    new-instance v1, Landroid/app/Notification$Action$Builder;

    const v2, 0x1080057

    const-string v3, "\u66f4\u6362\u56fe\u6807"

    invoke-direct {v1, v2, v3, v0}, Landroid/app/Notification$Action$Builder;-><init>(ILjava/lang/CharSequence;Landroid/app/PendingIntent;)V

    invoke-virtual {v1}, Landroid/app/Notification$Action$Builder;->build()Landroid/app/Notification$Action;

    move-result-object v0

    invoke-virtual {p0, v0}, Landroid/app/Notification$Builder;->addAction(Landroid/app/Notification$Action;)Landroid/app/Notification$Builder;
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :catch_0
    :cond_0
    return-void
.end method

.method public static apply(Landroid/app/Notification$Builder;I)Landroid/app/Notification$Builder;
    .locals 2

    :try_start_0
    invoke-static {}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->load()Landroid/graphics/Bitmap;

    move-result-object v0

    if-eqz v0, :cond_0

    invoke-static {v0}, Landroid/graphics/drawable/Icon;->createWithBitmap(Landroid/graphics/Bitmap;)Landroid/graphics/drawable/Icon;

    move-result-object v0

    invoke-virtual {p0, v0}, Landroid/app/Notification$Builder;->setSmallIcon(Landroid/graphics/drawable/Icon;)Landroid/app/Notification$Builder;
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_0

    :catch_0
    move-exception v0

    invoke-static {v0}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->log(Ljava/lang/Throwable;)V

    :cond_0
    invoke-virtual {p0, p1}, Landroid/app/Notification$Builder;->setSmallIcon(I)Landroid/app/Notification$Builder;

    :goto_0
    return-object p0
.end method

.method public static decode(Ljava/lang/String;)Landroid/graphics/Bitmap;
    .locals 5

    const/4 v0, 0x0

    :try_start_0
    new-instance v1, Ljava/io/FileInputStream;

    invoke-direct {v1, p0}, Ljava/io/FileInputStream;-><init>(Ljava/lang/String;)V

    invoke-static {v1}, Landroid/graphics/BitmapFactory;->decodeStream(Ljava/io/InputStream;)Landroid/graphics/Bitmap;

    move-result-object v0

    invoke-virtual {v1}, Ljava/io/FileInputStream;->close()V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_0

    :catch_0
    move-exception v1

    invoke-static {v1}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->log(Ljava/lang/Throwable;)V

    :goto_0
    return-object v0
.end method

.method public static handle(Landroid/app/Activity;IILandroid/content/Intent;)V
    .locals 3

    :try_start_0
    const/16 v0, 0x2768

    if-eq p1, v0, :cond_0

    return-void

    :cond_0
    const/4 v0, -0x1

    if-ne p2, v0, :cond_2

    if-eqz p3, :cond_2

    invoke-virtual {p3}, Landroid/content/Intent;->getData()Landroid/net/Uri;

    move-result-object v0

    if-eqz v0, :cond_2

    invoke-static {p0, v0}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->save(Landroid/content/Context;Landroid/net/Uri;)Z

    move-result v0

    if-eqz v0, :cond_1

    const-string v0, "\u901a\u77e5\u56fe\u6807\u5df2\u66f4\u65b0"

    invoke-static {v0}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->toast(Ljava/lang/String;)V

    goto :goto_0

    :cond_1
    const-string v0, "\u56fe\u6807\u4fdd\u5b58\u5931\u8d25"

    invoke-static {v0}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->toast(Ljava/lang/String;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :goto_0
    goto :goto_1

    :catch_0
    move-exception v0

    invoke-static {v0}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->log(Ljava/lang/Throwable;)V

    :cond_2
    :goto_1
    return-void
.end method

.method public static load()Landroid/graphics/Bitmap;
    .locals 5

    const/4 v0, 0x0

    :try_start_0
    const-string v1, "LOAD start"

    invoke-static {v1}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->logStr(Ljava/lang/String;)V

    const-string v1, "/data/data/com.tencent.mm/cache/eta_notify_icon.png"

    invoke-static {v1}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->decode(Ljava/lang/String;)Landroid/graphics/Bitmap;

    move-result-object v0

    if-nez v0, :cond_0

    const-string v1, "LOAD cache failed"

    invoke-static {v1}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->logStr(Ljava/lang/String;)V

    const-string v1, "/data/data/com.tencent.mm/Hchat/notify_icon.png"

    invoke-static {v1}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->decode(Ljava/lang/String;)Landroid/graphics/Bitmap;

    move-result-object v0

    if-eqz v0, :cond_0

    const-string v1, "LOAD Hchat ok"

    invoke-static {v1}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->logStr(Ljava/lang/String;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :catch_0
    :cond_0
    return-object v0
.end method

.method public static log(Ljava/lang/Throwable;)V
    .locals 2

    :try_start_0
    const-string v0, "Hchat:NotifyIcon"

    invoke-virtual {p0}, Ljava/lang/Throwable;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v0, v1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :catch_0
    return-void
.end method

.method public static logStr(Ljava/lang/String;)V
    .locals 1

    :try_start_0
    const-string v0, "Hchat:NotifyIcon"

    invoke-static {v0, p0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :catch_0
    return-void
.end method

.method public static reset()V
    .locals 3

    :try_start_0
    new-instance v0, Ljava/io/File;

    const-string v1, "/data/data/com.tencent.mm/Hchat/notify_icon.png"

    invoke-direct {v0, v1}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-virtual {v0}, Ljava/io/File;->exists()Z

    move-result v1

    if-eqz v1, :cond_0

    invoke-virtual {v0}, Ljava/io/File;->delete()Z

    :cond_0
    new-instance v0, Ljava/io/File;

    const-string v1, "/data/data/com.tencent.mm/cache/eta_notify_icon.png"

    invoke-direct {v0, v1}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-virtual {v0}, Ljava/io/File;->exists()Z

    move-result v1

    if-eqz v1, :cond_1

    invoke-virtual {v0}, Ljava/io/File;->delete()Z

    :cond_1
    const-string v0, "\u5df2\u6062\u590d\u9ed8\u8ba4\u901a\u77e5\u56fe\u6807"

    invoke-static {v0}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->toast(Ljava/lang/String;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :catch_0
    return-void
.end method

.method public static save(Landroid/content/Context;Landroid/net/Uri;)Z
    .locals 8

    const/4 v0, 0x0

    :try_start_0
    new-instance v1, Ljava/io/File;

    const-string v2, "/data/data/com.tencent.mm/Hchat"

    invoke-direct {v1, v2}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-virtual {v1}, Ljava/io/File;->exists()Z

    move-result v2

    if-nez v2, :cond_0

    invoke-virtual {v1}, Ljava/io/File;->mkdirs()Z

    :cond_0
    new-instance v2, Ljava/io/File;

    const-string v3, "/data/data/com.tencent.mm/Hchat/notify_icon.png"

    invoke-direct {v2, v3}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-virtual {p0}, Landroid/content/Context;->getContentResolver()Landroid/content/ContentResolver;

    move-result-object v3

    invoke-virtual {v3, p1}, Landroid/content/ContentResolver;->openInputStream(Landroid/net/Uri;)Ljava/io/InputStream;

    move-result-object v3

    new-instance v4, Ljava/io/FileOutputStream;

    invoke-direct {v4, v2}, Ljava/io/FileOutputStream;-><init>(Ljava/io/File;)V

    const/16 v5, 0x1000

    new-array v5, v5, [B

    :goto_0
    invoke-virtual {v3, v5}, Ljava/io/InputStream;->read([B)I

    move-result v6

    if-lez v6, :cond_1

    const/4 v7, 0x0

    invoke-virtual {v4, v5, v7, v6}, Ljava/io/FileOutputStream;->write([BII)V

    goto :goto_0

    :cond_1
    invoke-virtual {v3}, Ljava/io/InputStream;->close()V

    invoke-virtual {v4}, Ljava/io/FileOutputStream;->close()V

    const/4 v0, 0x1
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_1

    :catch_0
    move-exception v1

    invoke-static {v1}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->log(Ljava/lang/Throwable;)V

    :goto_1
    return v0
.end method

.method public static showToastNow(Ljava/lang/String;)V
    .locals 3

    :try_start_0
    invoke-static {}, Landroid/app/ActivityThread;->currentApplication()Landroid/app/Application;

    move-result-object v0

    const/4 v1, 0x1

    invoke-static {v0, p0, v1}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v0

    invoke-virtual {v0}, Landroid/widget/Toast;->show()V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :catch_0
    return-void
.end method

.method public static toast(Ljava/lang/String;)V
    .locals 3

    :try_start_0
    invoke-static {}, Landroid/os/Looper;->getMainLooper()Landroid/os/Looper;

    move-result-object v0

    new-instance v1, Landroid/os/Handler;

    invoke-direct {v1, v0}, Landroid/os/Handler;-><init>(Landroid/os/Looper;)V

    new-instance v0, Lh/Hchat/hooks/items/customnotify/EtaIconStore$ToastTask;

    invoke-direct {v0, p0}, Lh/Hchat/hooks/items/customnotify/EtaIconStore$ToastTask;-><init>(Ljava/lang/String;)V

    invoke-virtual {v1, v0}, Landroid/os/Handler;->post(Ljava/lang/Runnable;)Z
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :catch_0
    return-void
.end method
