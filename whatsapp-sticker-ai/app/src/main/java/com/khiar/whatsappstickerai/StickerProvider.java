package com.khiar.whatsappstickerai;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.database.Cursor;
import android.database.MatrixCursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import java.io.File;

public class StickerProvider extends ContentProvider {
    @Override public boolean onCreate() { return true; }
    @Override public String getType(Uri uri) { return "image/webp"; }
    @Override public Cursor query(Uri uri, String[] projection, String sel, String[] args, String sort) {
        String path = uri.getPath();
        if ("/metadata".equals(path)) {
            MatrixCursor c = new MatrixCursor(new String[]{"identifier","name","publisher","tray_image_file","avoid_cache","publisher_email","publisher_website","privacy_policy_website","license_agreement_website"});
            c.addRow(new Object[]{"ai_sticker_wa","AI Sticker WA","Khiar","tray.webp",0,"","","",""});
            return c;
        }
        if ("/stickers".equals(path)) {
            MatrixCursor c = new MatrixCursor(new String[]{"identifier","sticker_file_name","emojis","accessibility_text"});
            for (File f : StickerStore.all(getContext())) c.addRow(new Object[]{"ai_sticker_wa",f.getName(),"😀","AI Sticker"});
            return c;
        }
        return null;
    }
    @Override public ParcelFileDescriptor openFile(Uri uri, String mode) throws java.io.FileNotFoundException {
        String name = uri.getLastPathSegment();
        File f = new File(StickerStore.dir(getContext()), name);
        if (!f.exists() && "tray.webp".equals(name)) f = new File(getContext().getFilesDir(), "tray.webp");
        return ParcelFileDescriptor.open(f, ParcelFileDescriptor.MODE_READ_ONLY);
    }
    @Override public int delete(Uri u,String s,String[] a){return 0;}
    @Override public int update(Uri u,ContentValues v,String s,String[] a){return 0;}
    @Override public Uri insert(Uri u,ContentValues v){return null;}
}
