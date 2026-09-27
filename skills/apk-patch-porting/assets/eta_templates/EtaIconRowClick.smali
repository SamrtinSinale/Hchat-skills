.class public final Lh/Hchat/hooks/items/customnotify/EtaIconRowClick;
.super Ljava/lang/Object;

# interfaces
.implements L{{ROWCLICK}};


# instance fields
.field private final mode:I


# direct methods
.method public constructor <init>(I)V
    .locals 0

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput p1, p0, Lh/Hchat/hooks/items/customnotify/EtaIconRowClick;->mode:I

    return-void
.end method


# virtual methods
.method public final invoke()Ljava/lang/Object;
    .locals 2

    :try_start_0
    iget v0, p0, Lh/Hchat/hooks/items/customnotify/EtaIconRowClick;->mode:I

    if-nez v0, :cond_0

    invoke-static {}, Lh/Hchat/hooks/items/customnotify/EtaIconEntry;->pick()V

    goto :goto_0

    :cond_0
    invoke-static {}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->reset()V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :goto_0
    sget-object v0, L{{UNIT}};->a:L{{UNIT}};

    return-object v0

    :catch_0
    move-exception v0

    invoke-static {v0}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->log(Ljava/lang/Throwable;)V

    sget-object v0, L{{UNIT}};->a:L{{UNIT}};

    return-object v0
.end method
