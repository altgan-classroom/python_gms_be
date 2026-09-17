// reports-service (:5008): one endpoint, the report type is a path segment.
import { api } from '../api.js';

export const getReport = (locationId, report, from, to) =>
  api('reports', 'GET', `/locations/${locationId}/${report}`, {
    query: { report_date_from: from && `${from} 00:00`, report_date_to: to && `${to} 23:59` },
  });
