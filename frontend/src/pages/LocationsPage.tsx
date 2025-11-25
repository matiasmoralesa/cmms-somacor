import { Routes, Route } from 'react-router-dom';
import LocationList from '../components/locations/LocationList';
import LocationForm from '../components/locations/LocationForm';

const LocationsPage = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <Routes>
        <Route index element={<LocationList />} />
        <Route path="new" element={<LocationForm />} />
        <Route path=":id/edit" element={<LocationForm />} />
      </Routes>
    </div>
  );
};

export default LocationsPage;
