import brut.androlib.mod.SmaliMod;
import com.android.tools.smali.dexlib2.Opcodes;
import com.android.tools.smali.dexlib2.writer.builder.DexBuilder;
import com.android.tools.smali.dexlib2.writer.io.FileDataStore;
import java.io.File;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;

/** smali 树 -> dex 全量汇编。只有 fail==0 才写出 dex。 */
public class BuildDex {
    public static void main(String[] a) throws Exception {
        File root = new File(a[0]);
        File out  = new File(a[1]);
        int api = Integer.parseInt(a.length > 2 ? a[2] : "29");
        List<Path> files = Files.walk(root.toPath())
                .filter(p -> p.toString().endsWith(".smali"))
                .sorted().collect(Collectors.toList());
        System.out.println("smali files: " + files.size());
        DexBuilder db = new DexBuilder(new Opcodes(api, 0));
        int ok = 0, fail = 0;
        for (Path p : files) {
            try {
                if (SmaliMod.assembleSmaliFile(p.toFile(), db, api)) ok++;
                else { fail++; System.out.println("FAIL " + root.toPath().relativize(p)); }
            } catch (Throwable t) {
                fail++;
                System.out.println("ERR " + root.toPath().relativize(p) + " : " + t);
                if (fail > 8) break;
            }
        }
        System.out.println("ok=" + ok + " fail=" + fail);
        if (fail == 0) {
            FileDataStore ds = new FileDataStore(out);
            db.writeTo(ds);
            ds.raf.close();
            System.out.println("dex=" + out.length());
        }
    }
}
