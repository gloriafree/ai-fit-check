import { Routes, Route } from 'react-router-dom';
import { I18nProvider } from './i18n';
import AppShell from './components/layout/AppShell';
import LandingPage from './pages/LandingPage';
import BodyProfilePage from './pages/BodyProfilePage';
import CatalogPage from './pages/CatalogPage';
import ProductPage from './pages/ProductPage';
import ResultPage from './pages/ResultPage';

export default function App() {
  return (
    <I18nProvider>
      <AppShell>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/profile" element={<BodyProfilePage />} />
          <Route path="/catalog" element={<CatalogPage />} />
          <Route path="/product/:id" element={<ProductPage />} />
          <Route path="/result/:productId/:size" element={<ResultPage />} />
        </Routes>
      </AppShell>
    </I18nProvider>
  );
}
