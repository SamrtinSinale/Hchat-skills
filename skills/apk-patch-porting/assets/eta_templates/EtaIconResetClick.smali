.class public final Lh/Hchat/hooks/items/customnotify/EtaIconResetClick;
.super Ljava/lang/Object;

# interfaces
.implements L{{LAMBDA}};


# direct methods
.method public constructor <init>()V
    .locals 0

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public final invoke(Ljava/lang/Object;)Ljava/lang/Object;
    .locals 1

    :try_start_0
    invoke-static {}, Lh/Hchat/hooks/items/customnotify/EtaIconStore;->reset()V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :catch_0
    sget-object v0, L{{UNIT}};->a:L{{UNIT}};

    return-object v0
.end method
