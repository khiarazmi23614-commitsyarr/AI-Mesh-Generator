package com.khiar.whatsappstickerai;

import android.content.Context;
import android.graphics.Bitmap;
import java.io.File;
import java.io.FileOutputStream;
import java.util.ArrayList;
import java.util.List;

public final class StickerStore {
    private StickerStore() {}
    public static File dir(Context c) {
        File d = new File(c.getFilesDir(), "stickers");
        if (!d.exists()) d.mkdirs();
        return d;
    }
    public static void add(Context c, Bitmap b) throws Exception {
        File d = dir(c);
        File f = new File(d, "sticker_" + System.currentTimeMillis() + ".webp");
        try (FileOutputStream out = new FileOutputStream(f)) {
            b.compress(Bitmap.CompressFormat.WEBP_LOSSLESS, 100, out);
        }
    }
    public static List<File> all(Context c) {
        File[] fs = dir(c).listFiles((d,n) -> n.endsWith(".webp"));
        List<File> result = new ArrayList<>();
        if (fs != null) for (File f : fs) result.add(f);
        return result;
    }
}
