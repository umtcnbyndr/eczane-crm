import React, { useState, useEffect } from 'react';
import {
  ArrowUpTrayIcon,
  DocumentIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import { uploadExcel, getUploadHistory, generateTasks, updateSegments } from '../services/api';

const fileTypes = [
  { value: 'CUSTOMER_POINTS', label: 'Müşteri Puan Raporu', description: 'Müşterilerin Puan ve TL Karşılığı' },
  { value: 'PRODUCT_SALES', label: 'Ürün Satış Raporu', description: 'Grup Bazlı Ürün Satış Raporu' },
  { value: 'CUSTOMER_SALES', label: 'Müşteri Satış Raporu', description: 'Müşteri Ürün Satış Raporu' },
];

const statusColors = {
  PENDING: 'bg-yellow-100 text-yellow-700',
  PROCESSING: 'bg-blue-100 text-blue-700',
  COMPLETED: 'bg-green-100 text-green-700',
  FAILED: 'bg-red-100 text-red-700',
};

const statusIcons = {
  PENDING: ClockIcon,
  PROCESSING: ClockIcon,
  COMPLETED: CheckCircleIcon,
  FAILED: XCircleIcon,
};

function Upload() {
  const [file, setFile] = useState(null);
  const [fileType, setFileType] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const response = await getUploadHistory();
      setHistory(response.data);
    } catch (error) {
      console.error('Yükleme geçmişi alınamadı:', error);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setUploadResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file || !fileType) {
      alert('Lütfen dosya ve dosya tipini seçin');
      return;
    }

    setUploading(true);
    try {
      const response = await uploadExcel(file, fileType);
      setUploadResult({
        success: true,
        data: response.data,
      });
      setFile(null);
      setFileType('');
      loadHistory();
    } catch (error) {
      setUploadResult({
        success: false,
        error: error.response?.data?.error || 'Yükleme başarısız',
      });
    } finally {
      setUploading(false);
    }
  };

  const handleGenerateTasks = async () => {
    setProcessing(true);
    try {
      const response = await generateTasks();
      alert(`${response.data.tasks_created} görev oluşturuldu`);
    } catch (error) {
      alert('Görev oluşturma hatası');
    } finally {
      setProcessing(false);
    }
  };

  const handleUpdateSegments = async () => {
    setProcessing(true);
    try {
      const response = await updateSegments();
      alert(`${response.data.customers_updated} müşteri segmenti güncellendi`);
    } catch (error) {
      alert('Segment güncelleme hatası');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="space-y-6 pb-20 lg:pb-0">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Veri Yükle</h1>
        <p className="text-gray-500">Excel dosyalarını yükleyin</p>
      </div>

      {/* Upload Form */}
      <div className="bg-white rounded-2xl border p-6 shadow-sm">
        <h2 className="font-bold text-lg mb-4">Excel Yükle</h2>

        {/* File Type Selection */}
        <div className="space-y-3 mb-4">
          <label className="block text-sm font-medium text-gray-700">Dosya Tipi</label>
          {fileTypes.map((type) => (
            <label
              key={type.value}
              className={`flex items-center p-3 rounded-xl border-2 cursor-pointer transition-colors ${
                fileType === type.value
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <input
                type="radio"
                name="fileType"
                value={type.value}
                checked={fileType === type.value}
                onChange={(e) => setFileType(e.target.value)}
                className="sr-only"
              />
              <div>
                <p className="font-medium">{type.label}</p>
                <p className="text-sm text-gray-500">{type.description}</p>
              </div>
            </label>
          ))}
        </div>

        {/* File Input */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Dosya Seç</label>
          <div
            className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
              file ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input
              type="file"
              accept=".xlsx,.xls,.csv"
              onChange={handleFileChange}
              className="hidden"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              {file ? (
                <div className="flex items-center justify-center gap-2">
                  <DocumentIcon className="w-8 h-8 text-primary-600" />
                  <span className="font-medium text-primary-600">{file.name}</span>
                </div>
              ) : (
                <>
                  <ArrowUpTrayIcon className="w-12 h-12 mx-auto text-gray-400 mb-2" />
                  <p className="text-gray-600">Dosya seçmek için tıklayın</p>
                  <p className="text-sm text-gray-400 mt-1">.xlsx, .xls veya .csv</p>
                </>
              )}
            </label>
          </div>
        </div>

        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={!file || !fileType || uploading}
          className="w-full py-3 rounded-xl bg-primary-600 text-white font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {uploading ? (
            <span className="flex items-center justify-center gap-2">
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Yükleniyor...
            </span>
          ) : (
            'Yükle'
          )}
        </button>

        {/* Upload Result */}
        {uploadResult && (
          <div
            className={`mt-4 p-4 rounded-xl ${
              uploadResult.success ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
            }`}
          >
            {uploadResult.success ? (
              <div className="flex items-center gap-2">
                <CheckCircleIcon className="w-5 h-5" />
                <span>
                  Başarılı! {uploadResult.data.rows_processed} satır işlendi.
                </span>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <XCircleIcon className="w-5 h-5" />
                <span>{uploadResult.error}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="bg-white rounded-2xl border p-6 shadow-sm">
        <h2 className="font-bold text-lg mb-4">Aksiyonlar</h2>
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={handleGenerateTasks}
            disabled={processing}
            className="py-3 px-4 rounded-xl bg-blue-100 text-blue-700 font-medium hover:bg-blue-200 disabled:opacity-50 transition-colors"
          >
            Görevleri Oluştur
          </button>
          <button
            onClick={handleUpdateSegments}
            disabled={processing}
            className="py-3 px-4 rounded-xl bg-purple-100 text-purple-700 font-medium hover:bg-purple-200 disabled:opacity-50 transition-colors"
          >
            Segmentleri Güncelle
          </button>
        </div>
      </div>

      {/* Upload History */}
      <div className="bg-white rounded-2xl border p-6 shadow-sm">
        <h2 className="font-bold text-lg mb-4">Yükleme Geçmişi</h2>
        {history.length === 0 ? (
          <p className="text-gray-500 text-center py-4">Henüz yükleme yok</p>
        ) : (
          <div className="space-y-3">
            {history.map((upload) => {
              const StatusIcon = statusIcons[upload.status];
              return (
                <div key={upload.id} className="flex items-center gap-3 p-3 rounded-xl bg-gray-50">
                  <StatusIcon className={`w-5 h-5 ${statusColors[upload.status].split(' ')[1]}`} />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">{upload.file_name}</p>
                    <p className="text-xs text-gray-500">{upload.file_type_display}</p>
                  </div>
                  <div className="text-right">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[upload.status]}`}>
                      {upload.status_display}
                    </span>
                    <p className="text-xs text-gray-400 mt-1">
                      {upload.rows_processed} satır
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default Upload;
