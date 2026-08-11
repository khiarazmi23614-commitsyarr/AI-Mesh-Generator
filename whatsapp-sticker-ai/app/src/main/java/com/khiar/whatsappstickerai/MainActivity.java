package com.khiar.whatsappstickerai;

import android.content.ContentValues;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends AppCompatActivity {
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private EditText keyInput, promptInput;
    private ImageView preview;
    private Bitmap sticker;

    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        buildUi();
    }

    private void buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(32, 40, 32, 24);

        TextView title = new TextView(this);
        title.setText("AI Sticker WA"); title.setTextSize(28); title.setTextAlignment(TextView.TEXT_ALIGNMENT_CENTER);
        root.addView(title, new LinearLayout.LayoutParams(-1, -2));

        TextView info = new TextView(this);
        info.setText("Buat stiker dari prompt dengan background transparan."); info.setTextSize(15); info.setPadding(0, 8, 0, 18);
        root.addView(info, new LinearLayout.LayoutParams(-1, -2));

        keyInput = new EditText(this); keyInput.setHint("OpenAI API key (disimpan hanya di HP)"); keyInput.setSingleLine(true); keyInput.setInputType(0x81);
        root.addView(keyInput, new LinearLayout.LayoutParams(-1, -2));

        promptInput = new EditText(this); promptInput.setHint("Contoh: kucing oren tertawa sambil jempol"); promptInput.setMinLines(2);
        root.addView(promptInput, new LinearLayout.LayoutParams(-1, -2));

        Button generate = new Button(this); generate.setText("✨ Buat Stiker AI"); root.addView(generate);

        preview = new ImageView(this); preview.setAdjustViewBounds(true); preview.setScaleType(ImageView.ScaleType.CENTER_INSIDE);
        LinearLayout.LayoutParams pp = new LinearLayout.LayoutParams(-1, 0, 1); pp.topMargin = 12; root.addView(preview, pp);

        LinearLayout actions = new LinearLayout(this); actions.setOrientation(LinearLayout.HORIZONTAL);
        Button save = new Button(this); save.setText("Simpan PNG"); Button wa = new Button(this); wa.setText("Kirim ke WhatsApp");
        actions.addView(save, new LinearLayout.LayoutParams(0, -2, 1)); actions.addView(wa, new LinearLayout.LayoutParams(0, -2, 1)); root.addView(actions);
        setContentView(root);

        generate.setOnClickListener(v -> generateSticker());
        save.setOnClickListener(v -> saveSticker());
        wa.setOnClickListener(v -> shareToWhatsApp());
    }

    private void generateSticker() {
        String key = keyInput.getText().toString().trim(); String prompt = promptInput.getText().toString().trim();
        if (key.isEmpty() || prompt.isEmpty()) { Toast.makeText(this, "Isi API key dan prompt dulu.", Toast.LENGTH_SHORT).show(); return; }
        Toast.makeText(this, "Sedang membuat stiker...", Toast.LENGTH_SHORT).show();
        executor.execute(() -> {
            try {
                URL u = new URL("https://api.openai.com/v1/images/generations");
                HttpURLConnection c = (HttpURLConnection) u.openConnection(); c.setRequestMethod("POST"); c.setDoOutput(true);
                c.setRequestProperty("Authorization", "Bearer " + key); c.setRequestProperty("Content-Type", "application/json");
                JSONObject body = new JSONObject(); body.put("model", "gpt-image-1");
                body.put("prompt", "Create a WhatsApp sticker. Subject: " + prompt + ". Centered character/object, clean bold outline, expressive, simple sticker composition, transparent background, no watermark. Keep the whole subject inside the canvas.");
                body.put("background", "transparent"); body.put("output_format", "png"); body.put("size", "1024x1024"); body.put("quality", "auto");
                try (OutputStream os = c.getOutputStream()) { os.write(body.toString().getBytes(StandardCharsets.UTF_8)); }
                int code = c.getResponseCode(); InputStream is = code >= 400 ? c.getErrorStream() : c.getInputStream();
                String response = new String(readAll(is), StandardCharsets.UTF_8); c.disconnect();
                if (code >= 400) throw new Exception("API error " + code + ": " + response);
                JSONObject json = new JSONObject(response); String b64 = json.getJSONArray("data").getJSONObject(0).getString("b64_json");
                byte[] bytes = Base64.decode(b64, Base64.DEFAULT); Bitmap bm = BitmapFactory.decodeByteArray(bytes, 0, bytes.length);
                runOnUiThread(() -> { sticker = bm; preview.setImageBitmap(bm); Toast.makeText(this, "Stiker selesai!", Toast.LENGTH_SHORT).show(); });
            } catch (Exception e) { runOnUiThread(() -> Toast.makeText(this, "Gagal: " + e.getMessage(), Toast.LENGTH_LONG).show()); }
        });
    }

    private byte[] readAll(InputStream in) throws Exception { ByteArrayOutputStream out = new ByteArrayOutputStream(); byte[] buf = new byte[8192]; int n; while ((n = in.read(buf)) != -1) out.write(buf, 0, n); return out.toByteArray(); }

    private Uri saveSticker() {
        if (sticker == null) { Toast.makeText(this, "Buat stiker dulu.", Toast.LENGTH_SHORT).show(); return null; }
        try {
            ContentValues v = new ContentValues(); v.put(MediaStore.Images.Media.DISPLAY_NAME, "ai_sticker_" + System.currentTimeMillis() + ".png"); v.put(MediaStore.Images.Media.MIME_TYPE, "image/png"); v.put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES + "/AI Sticker WA");
            Uri uri = getContentResolver().insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, v); if (uri == null) throw new Exception("Tidak bisa membuat file");
            try (OutputStream os = getContentResolver().openOutputStream(uri)) { sticker.compress(Bitmap.CompressFormat.PNG, 100, os); }
            Toast.makeText(this, "PNG disimpan.", Toast.LENGTH_SHORT).show(); return uri;
        } catch (Exception e) { Toast.makeText(this, "Gagal menyimpan: " + e.getMessage(), Toast.LENGTH_LONG).show(); return null; }
    }

    private void shareToWhatsApp() {
        Uri uri = saveSticker(); if (uri == null) return;
        Intent i = new Intent(Intent.ACTION_SEND); i.setType("image/png"); i.putExtra(Intent.EXTRA_STREAM, uri); i.setPackage("com.whatsapp"); i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        try { startActivity(i); } catch (Exception e) { Toast.makeText(this, "WhatsApp tidak ditemukan. PNG sudah disimpan.", Toast.LENGTH_LONG).show(); }
    }

    @Override protected void onDestroy() { executor.shutdownNow(); super.onDestroy(); }
}
