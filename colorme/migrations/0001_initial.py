# Generated by Django 3.0.2 on 2020-02-09 14:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_id', models.CharField(max_length=100, unique=True, verbose_name='商品ID')),
                ('category_1', models.CharField(blank=True, max_length=100, null=True, verbose_name='カテゴリ(大)')),
                ('category_2', models.CharField(blank=True, max_length=100, null=True, verbose_name='カテゴリ(小)')),
                ('kataban', models.CharField(blank=True, max_length=100, null=True, verbose_name='型番')),
                ('item_name', models.CharField(max_length=255, verbose_name='商品名')),
                ('image_url', models.URLField(blank=True, max_length=255, null=True, verbose_name='商品画像URL')),
                ('create_feature_phone_image', models.CharField(max_length=100, verbose_name='フィーチャーフォン向け画像作成')),
                ('extra_image_1_url', models.URLField(blank=True, max_length=255, null=True, verbose_name='その他画像1URL')),
                ('extra_image_2_url', models.URLField(blank=True, max_length=255, null=True, verbose_name='その他画像2URL')),
                ('extra_image_3_url', models.URLField(blank=True, max_length=255, null=True, verbose_name='その他画像3URL')),
                ('extra_image_4_url', models.URLField(blank=True, max_length=255, null=True, verbose_name='その他画像4URL')),
                ('extra_image_5_url', models.URLField(blank=True, max_length=255, null=True, verbose_name='その他画像5URL')),
                ('extra_image_6_url', models.URLField(blank=True, max_length=255, null=True, verbose_name='その他画像6URL')),
                ('extra_image_7_url', models.URLField(blank=True, max_length=255, null=True, verbose_name='その他画像7URL')),
                ('extra_image_8_url', models.URLField(blank=True, max_length=255, null=True, verbose_name='その他画像8URL')),
                ('extra_image_9_url', models.URLField(blank=True, max_length=255, null=True, verbose_name='その他画像9URL')),
                ('sell_price', models.IntegerField(verbose_name='販売価格')),
                ('member_price', models.IntegerField(verbose_name='会員価格')),
                ('regular_price', models.IntegerField(blank=True, null=True, verbose_name='定価')),
                ('cost_price', models.IntegerField(blank=True, null=True, verbose_name='原価')),
                ('stock_count', models.IntegerField(verbose_name='在庫数')),
                ('manage_stock', models.CharField(max_length=100, verbose_name='在庫管理')),
                ('min_purchase_qty', models.IntegerField(blank=True, null=True, verbose_name='最小購入数量')),
                ('max_purchase_qty', models.IntegerField(blank=True, null=True, verbose_name='最大購入数量')),
                ('sale_start_date', models.DateField(blank=True, null=True, verbose_name='販売開始日付')),
                ('sale_start_time', models.TimeField(blank=True, null=True, verbose_name='販売開始時間')),
                ('sale_end_date', models.DateField(blank=True, null=True, verbose_name='販売終了日付')),
                ('sale_end_time', models.TimeField(blank=True, null=True, verbose_name='販売終了時間')),
                ('unit', models.CharField(blank=True, max_length=100, null=True, verbose_name='単位')),
                ('weight', models.FloatField(blank=True, null=True, verbose_name='重量')),
                ('outstock_message', models.CharField(blank=True, max_length=100, null=True, verbose_name='売り切れ時メッセージ')),
                ('optimal_stock_count', models.IntegerField(blank=True, null=True, verbose_name='適正在庫数')),
                ('display_seq', models.IntegerField(blank=True, null=True, verbose_name='表示順')),
                ('short_description', models.CharField(blank=True, max_length=255, null=True, verbose_name='簡易説明')),
                ('description', models.TextField(verbose_name='商品説明')),
                ('description_for_feature_phone_shop', models.TextField(blank=True, null=True, verbose_name='フィーチャーフォン向けショップ用商品説明')),
                ('description_for_smartphone_shop', models.TextField(blank=True, null=True, verbose_name='スマートフォン向けショップ用商品説明')),
                ('use_new_mark', models.CharField(max_length=100, verbose_name='Newマーク付加設定')),
                ('new_mark_image', models.IntegerField(blank=True, null=True, verbose_name='Newマーク画像')),
                ('ad_category_id', models.IntegerField(blank=True, null=True, verbose_name='広告用カテゴリID')),
                ('ad_tag_1', models.CharField(blank=True, max_length=100, null=True, verbose_name='広告用タグ1')),
                ('ad_tag_2', models.CharField(blank=True, max_length=100, null=True, verbose_name='広告用タグ2')),
                ('ad_tag_3', models.CharField(blank=True, max_length=100, null=True, verbose_name='広告用タグ3')),
                ('ad_description', models.CharField(blank=True, max_length=255, null=True, verbose_name='広告用商品説明')),
                ('brand', models.CharField(blank=True, max_length=255, null=True, verbose_name='ブランド')),
                ('jan_isbn', models.CharField(blank=True, max_length=100, null=True, verbose_name='JAN/ISBN')),
                ('mpn', models.CharField(blank=True, max_length=100, null=True, verbose_name='MPN')),
                ('condition', models.CharField(blank=True, max_length=100, null=True, verbose_name='状態')),
                ('gender', models.CharField(blank=True, max_length=100, null=True, verbose_name='性別')),
                ('color', models.CharField(blank=True, max_length=100, null=True, verbose_name='色')),
                ('size', models.CharField(blank=True, max_length=100, null=True, verbose_name='サイズ')),
                ('title', models.CharField(blank=True, max_length=100, null=True, verbose_name='タイトル')),
                ('keyword', models.CharField(blank=True, max_length=100, null=True, verbose_name='キーワード')),
                ('page_abstract', models.CharField(blank=True, max_length=255, null=True, verbose_name='ページ概要')),
                ('transfer_fee', models.IntegerField(blank=True, null=True, verbose_name='個別送料')),
                ('display_status', models.CharField(max_length=100, verbose_name='掲載設定')),
                ('discount_tax_rate', models.CharField(max_length=100, verbose_name='軽減税率設定')),
                ('option_1_name', models.CharField(blank=True, max_length=100, null=True)),
                ('option_2_name', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_name', models.CharField(choices=[('import_csv', 'CSV取り込み'), ('sync_thebase', 'BASEへ反映'), ('sync_wowma', 'WOWMAへ反映')], max_length=255)),
                ('registered_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='1', max_length=100)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('log', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_1_value', models.CharField(max_length=100)),
                ('option_2_value', models.CharField(blank=True, max_length=100, null=True)),
                ('option_id', models.CharField(max_length=100)),
                ('kataban', models.CharField(blank=True, max_length=100, null=True)),
                ('stock_count', models.IntegerField(blank=True, null=True)),
                ('optimal_stock_count', models.IntegerField(blank=True, null=True)),
                ('sale_price', models.IntegerField(blank=True, null=True)),
                ('member_price', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UploadFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('csv_file', models.FileField(upload_to='uploaded', verbose_name='product.csv')),
                ('file_type', models.CharField(choices=[('0', 'product.csv'), ('1', 'optino.csv')], max_length=100)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='登録日')),
                ('processed_at', models.DateTimeField(blank=True, null=True, verbose_name='処理日')),
            ],
        ),
        migrations.CreateModel(
            name='UploadFileErrorRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line_number', models.IntegerField(verbose_name='行番号')),
                ('error_message', models.CharField(blank=True, max_length=255, null=True, verbose_name='エラー')),
                ('parent_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='errors', to='colorme.UploadFile', verbose_name='親ファイル')),
            ],
        ),
    ]
