.class public final Lh/Hchat/hooks/items/customnotify/EtaIconStore$ToastTask;
.super Ljava/lang/Object;

# interfaces
.implements Ljava/lang/Runnable;


# instance fields
.field public final msg:Ljava/lang/String;


# direct methods
.method public constructor <init>(Ljava/lang/String;)V
    .locals 0

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lh/Hchat/hooks/items/customnotify/EtaIconStore$ToastTask;->msg:Ljava/lang/String;

    return-void
.end method


# virtual methods
.method public final run()V
    .locals 1

    iget-object v0, p0, Lh/Hchat/hooks/items/customnotify/EtaIconStore$ToastTask;->msg:Ljava/lang/String;

    invoke-static {v0}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->showToastNow(Ljava/lang/String;)V

    return-void
.end method
