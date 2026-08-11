package com.khiar.whatsappstickerai;

import android.app.Activity;
import android.content.Intent;
import android.graphics.*;
import android.net.Uri;
import android.os.Bundle;
import android.provider.Settings;
import android.view.Gravity;
import android.widget.*;
import java.io.InputStream;

public class MainActivity extends Activity {
    private static final int PICK=10;
    private Bitmap current;
    private ImageView preview;
    private TextView status;

    @Override public void onCreate(Bundle b){super.onCreate(b); build();}
    private void build(){
        LinearLayout root=new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL); root.setPadding(28,35,28,25);
        TextView title=new TextView(this); title.setText("AI Sticker WA"); title.setTextSize(28); title.setGravity(Gravity.CENTER); root.addView(title,new LinearLayout.LayoutParams(-1,-2));
        status=new TextView(this); status.setText("Tekan + untuk memilih foto"); status.setGravity(Gravity.CENTER); status.setPadding(0,10,0,12); root.addView(status,new LinearLayout.LayoutParams(-1,-2));
        Button add=new Button(this); add.setText("＋  Tambah Foto"); root.addView(add,new LinearLayout.LayoutParams(-1,-2));
        preview=new ImageView(this); preview.setAdjustViewBounds(true); preview.setScaleType(ImageView.ScaleType.CENTER_INSIDE); LinearLayout.LayoutParams pp=new LinearLayout.LayoutParams(-1,0,1); pp.topMargin=12; root.addView(preview,pp);
        LinearLayout row=new LinearLayout(this); row.setOrientation(LinearLayout.HORIZONTAL);
        Button edit=new Button(this); edit.setText("Edit"); Button direct=new Button(this); direct.setText("Langsung Jadi Stiker"); row.addView(edit,new LinearLayout.LayoutParams(0,-2,1)); row.addView(direct,new LinearLayout.LayoutParams(0,-2,1)); root.addView(row);
        Button save=new Button(this); save.setText("💚 Simpan ke WhatsApp"); root.addView(save,new LinearLayout.LayoutParams(-1,-2));
        setContentView(root);
        add.setOnClickListener(v->pick()); edit.setOnClickListener(v->editDialog()); direct.setOnClickListener(v->makeSticker()); save.setOnClickListener(v->saveToWhatsApp());
    }
    private void pick(){Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.setType("image/*");i.addCategory(Intent.CATEGORY_OPENABLE);startActivityForResult(i,PICK);}
    @Override protected void onActivityResult(int r,int c,Intent d){super.onActivityResult(r,c,d);if(r==PICK&&c==RESULT_OK&&d!=null){try(InputStream in=getContentResolver().openInputStream(d.getData())){current=BitmapFactory.decodeStream(in);preview.setImageBitmap(current);status.setText("Foto siap. Pilih Edit atau Langsung Jadi Stiker.");}catch(Exception e){toast("Gagal membuka foto");}}}
    private Bitmap square(Bitmap src){int s=Math.min(src.getWidth(),src.getHeight());Bitmap out=Bitmap.createBitmap(512,512,Bitmap.Config.ARGB_8888);Canvas c=new Canvas(out);c.drawColor(Color.TRANSPARENT,PorterDuff.Mode.CLEAR);float scale=470f/s;Matrix m=new Matrix();m.setScale(scale,scale);m.postTranslate((512-src.getWidth()*scale)/2f,(512-src.getHeight()*scale)/2f);Paint p=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);c.drawBitmap(src,m,p);return out;}
    private void makeSticker(){if(current==null){toast("Tambahkan foto dulu");return;}try{Bitmap b=square(current);StickerStore.add(this,b);createTray(b);toast("Stiker ditambahkan ke paket");}catch(Exception e){toast("Gagal membuat stiker");}}
    private void editDialog(){if(current==null){toast("Tambahkan foto dulu");return;} LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL); EditText text=new EditText(this);text.setHint("Teks stiker (opsional)");box.addView(text); Button bg=new Button(this);bg.setText("Hilangkan Background");box.addView(bg);bg.setOnClickListener(v->{current=removeBackground(current);preview.setImageBitmap(current);}); new android.app.AlertDialog.Builder(this).setTitle("Edit Stiker").setView(box).setPositiveButton("Simpan",(d,w)->{String t=text.getText().toString().trim();if(!t.isEmpty())current=addText(current,t);preview.setImageBitmap(current);makeSticker();}).setNegativeButton("Batal",null).show();}
    private Bitmap addText(Bitmap src,String text){Bitmap b=src.copy(Bitmap.Config.ARGB_8888,true);Canvas c=new Canvas(b);Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);p.setTextAlign(Paint.Align.CENTER);p.setTextSize(Math.max(36,b.getWidth()/9f));p.setTypeface(Typeface.DEFAULT_BOLD);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(10);p.setColor(Color.WHITE);c.drawText(text,b.getWidth()/2f,b.getHeight()-35,p);p.setStyle(Paint.Style.FILL);p.setColor(Color.BLACK);c.drawText(text,b.getWidth()/2f,b.getHeight()-35,p);return b;}
    private Bitmap removeBackground(Bitmap src){Bitmap b=src.copy(Bitmap.Config.ARGB_8888,true);int w=b.getWidth(),h=b.getHeight();int bg=b.getPixel(0,0);int br=Color.red(bg),bgc=Color.green(bg),bb=Color.blue(bg);int[] px=new int[w*h];b.getPixels(px,0,w,0,0,w,h);for(int y=0;y<h;y++)for(int x=0;x<w;x++){int i=y*w+x,c=px[i];int dist=Math.abs(Color.red(c)-br)+Math.abs(Color.green(c)-bgc)+Math.abs(Color.blue(c)-bb);if(dist<55)px[i]=Color.TRANSPARENT;}b.setPixels(px,0,w,0,0,w,h);return b;}
    private void createTray(Bitmap b){try{Bitmap t=Bitmap.createScaledBitmap(b,96,96,true);java.io.File f=new java.io.File(getFilesDir(),"tray.webp");try(java.io.FileOutputStream o=new java.io.FileOutputStream(f)){t.compress(Bitmap.CompressFormat.WEBP_LOSSLESS,100,o);}}catch(Exception ignored){}}
    private void saveToWhatsApp(){if(StickerStore.all(this).isEmpty()){toast("Buat minimal 1 stiker dulu");return;}Intent i=new Intent("com.whatsapp.intent.action.ENABLE_STICKER_PACK");i.putExtra("sticker_pack_id","ai_sticker_wa");i.putExtra("sticker_pack_authority","com.khiar.whatsappstickerai.stickercontentprovider");i.putExtra("sticker_pack_name","AI Sticker WA");try{startActivity(i);}catch(Exception e){toast("WhatsApp tidak mendukung pemasangan paket ini di perangkat ini.");}}
    private void toast(String s){Toast.makeText(this,s,Toast.LENGTH_SHORT).show();}
}
