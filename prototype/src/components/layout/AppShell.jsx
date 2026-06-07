import Header from './Header';
import BottomNav from './BottomNav';

export default function AppShell({ children }) {
  return (
    <div className="max-w-md mx-auto min-h-screen flex flex-col bg-cream shadow-lg relative">
      <Header />
      <main className="flex-1 overflow-y-auto pb-20">{children}</main>
      <BottomNav />
    </div>
  );
}
