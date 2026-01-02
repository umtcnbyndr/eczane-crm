import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  MagnifyingGlassIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import { getProducts } from '../services/api';

const categoryColors = {
  ILAC: 'bg-blue-100 text-blue-700',
  DERMO: 'bg-pink-100 text-pink-700',
  VITAMIN: 'bg-green-100 text-green-700',
  OTC: 'bg-purple-100 text-purple-700',
  MAMA: 'bg-yellow-100 text-yellow-700',
  OTHER: 'bg-gray-100 text-gray-700',
};

function ProductCard({ product }) {
  const isLowStock = product.stock_quantity <= 10;

  return (
    <div className="bg-white rounded-xl border p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-2">
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${categoryColors[product.category]}`}>
          {product.category_display}
        </span>
        {isLowStock && (
          <span className="flex items-center gap-1 text-xs text-red-500">
            <ExclamationTriangleIcon className="w-4 h-4" />
            Düşük Stok
          </span>
        )}
      </div>

      <h3 className="font-semibold text-gray-900 line-clamp-2">{product.name}</h3>

      {product.brand_name && (
        <p className="text-xs text-primary-600 font-medium mt-1">{product.brand_name}</p>
      )}
      <p className="text-xs text-gray-400 mt-1">Barkod: {product.barcode}</p>

      <div className="flex items-center justify-between mt-3 pt-3 border-t">
        <div>
          <p className="text-xs text-gray-500">Stok</p>
          <p className={`font-bold ${isLowStock ? 'text-red-600' : 'text-gray-900'}`}>
            {product.stock_quantity} adet
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-500">Fiyat</p>
          <p className="font-bold text-gray-900">
            {parseFloat(product.unit_price).toLocaleString('tr-TR', {
              style: 'currency',
              currency: 'TRY'
            })}
          </p>
        </div>
      </div>
    </div>
  );
}

function Products() {
  const [searchParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [lowStock, setLowStock] = useState(searchParams.get('low_stock') === 'true');

  useEffect(() => {
    loadProducts();
  }, [category, lowStock]);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const params = {};
      if (category) params.category = category;
      if (search) params.search = search;
      if (lowStock) params.low_stock = 'true';

      const response = await getProducts(params);
      setProducts(response.data.results || response.data);
    } catch (error) {
      console.error('Ürünler yüklenemedi:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadProducts();
  };

  return (
    <div className="space-y-6 pb-20 lg:pb-0">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Ürünler</h1>
        <p className="text-gray-500">{products.length} ürün listelendi</p>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="relative">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Ürün adı veya barkod ara..."
          className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none"
        />
      </form>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setLowStock(!lowStock)}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
            lowStock
              ? 'bg-red-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Düşük Stok
        </button>
        {['', 'ILAC', 'DERMO', 'VITAMIN', 'OTC'].map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat)}
            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              category === cat
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {cat ? cat : 'Tüm Kategoriler'}
          </button>
        ))}
      </div>

      {/* Product List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : products.length === 0 ? (
        <div className="bg-white rounded-2xl p-8 text-center shadow-sm border">
          <p className="text-gray-500">Ürün bulunamadı</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
}

export default Products;
