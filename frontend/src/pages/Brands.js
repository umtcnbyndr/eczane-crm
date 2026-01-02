import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  MagnifyingGlassIcon,
  StarIcon,
  CubeIcon,
} from '@heroicons/react/24/outline';
import { StarIcon as StarSolidIcon } from '@heroicons/react/24/solid';
import { getBrands } from '../services/api';

const categoryColors = {
  DERMO: 'bg-pink-100 text-pink-700',
  ILAC: 'bg-blue-100 text-blue-700',
  VITAMIN: 'bg-green-100 text-green-700',
  MAMA: 'bg-yellow-100 text-yellow-700',
  OTHER: 'bg-gray-100 text-gray-700',
};

const categoryNames = {
  DERMO: 'Dermo-Kozmetik',
  ILAC: 'İlaç',
  VITAMIN: 'Vitamin/Takviye',
  MAMA: 'Mama',
  OTHER: 'Diğer',
};

function BrandCard({ brand }) {
  return (
    <Link
      to={`/products?brand=${brand.id}`}
      className="bg-white rounded-xl border p-5 hover:shadow-lg transition-all hover:border-primary-300"
    >
      <div className="flex items-start justify-between mb-3">
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${categoryColors[brand.category]}`}>
          {categoryNames[brand.category]}
        </span>
        {brand.is_premium && (
          <span className="flex items-center gap-1 text-xs text-amber-500">
            <StarSolidIcon className="w-4 h-4" />
            Premium
          </span>
        )}
      </div>

      <h3 className="text-lg font-bold text-gray-900 mb-2">{brand.name}</h3>

      <div className="flex items-center gap-2 text-gray-500">
        <CubeIcon className="w-4 h-4" />
        <span className="text-sm">{brand.product_count} ürün</span>
      </div>
    </Link>
  );
}

function Brands() {
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');

  useEffect(() => {
    loadBrands();
  }, [category]);

  const loadBrands = async () => {
    setLoading(true);
    try {
      const params = {};
      if (category) params.category = category;

      const response = await getBrands(params);
      let data = response.data.results || response.data;

      // Filter by search
      if (search) {
        data = data.filter(b =>
          b.name.toLowerCase().includes(search.toLowerCase())
        );
      }

      setBrands(data);
    } catch (error) {
      console.error('Markalar yüklenemedi:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadBrands();
  };

  const filteredBrands = search
    ? brands.filter(b => b.name.toLowerCase().includes(search.toLowerCase()))
    : brands;

  const premiumBrands = filteredBrands.filter(b => b.is_premium);
  const regularBrands = filteredBrands.filter(b => !b.is_premium);

  return (
    <div className="space-y-6 pb-20 lg:pb-0">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Markalar</h1>
        <p className="text-gray-500">{filteredBrands.length} marka listelendi</p>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="relative">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Marka ara..."
          className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none"
        />
      </form>

      {/* Category Filters */}
      <div className="flex flex-wrap gap-2">
        {['', 'DERMO', 'VITAMIN', 'ILAC', 'MAMA'].map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat)}
            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              category === cat
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {cat ? categoryNames[cat] : 'Tümü'}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : filteredBrands.length === 0 ? (
        <div className="bg-white rounded-2xl p-8 text-center shadow-sm border">
          <p className="text-gray-500">Marka bulunamadı</p>
          <p className="text-sm text-gray-400 mt-2">
            Markalar, ürünler yüklendiğinde otomatik algılanır.
          </p>
        </div>
      ) : (
        <>
          {/* Premium Brands */}
          {premiumBrands.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <StarSolidIcon className="w-5 h-5 text-amber-500" />
                Premium Markalar
              </h2>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {premiumBrands.map((brand) => (
                  <BrandCard key={brand.id} brand={brand} />
                ))}
              </div>
            </div>
          )}

          {/* Regular Brands */}
          {regularBrands.length > 0 && (
            <div>
              {premiumBrands.length > 0 && (
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Diğer Markalar</h2>
              )}
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {regularBrands.map((brand) => (
                  <BrandCard key={brand.id} brand={brand} />
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Brands;
